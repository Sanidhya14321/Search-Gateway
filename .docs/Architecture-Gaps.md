# CRMind — Architecture Gaps & Design Decisions

This document explains every non-obvious architectural decision and the gaps
that were found and resolved during design review.

---

## Gap 1 — Embedding Model Versioning [CRITICAL]

**Risk:** Switching models (Ollama → OpenAI) makes all vectors invalid.
Cosine similarity between different model vectors = meaningless. No error — silent wrong results.

**Fix:**
- `chunks.embed_model_id VARCHAR(64)` stores the model on every row
- Every `vector_search` query filters `WHERE embed_model_id = $current_model`
- `scripts/rembed_chunks.py` re-embeds all chunks with new model before switching
- Alembic migration `002` adds the columns

**Upgrade procedure:**
```bash
python scripts/rembed_chunks.py --model text-embedding-3-small --dry-run
python scripts/rembed_chunks.py --model text-embedding-3-small
# verify all chunks updated, then update settings.embedding_model and deploy
```

---

## Gap 2 — No Retry / Circuit Breaker [CRITICAL]

**Risk:** Ollama crashes → entire request fails with unhandled exception.

**Fix:** `tenacity` decorators + `CircuitBreaker` class in `backend/utils/`.

Degradation chain:
```
LLM available → full synthesis
Circuit OPEN → template_fallback(top-3 chunks as bullets)
Stale cache hit → cached result + stale=true
All fail → {degraded:true, raw_chunks:[...]}
```

Never return HTTP 500 when partial results exist.

---

## Gap 3 — No Pagination [CRITICAL]

**Risk:** Unbounded queries OOM or time out at scale.

**Fix:** `PaginatedResponse[T]` generic in `models/responses.py`.
Every list endpoint accepts `limit` (max 100) + `offset`, returns `total`/`has_more`.
Vector search `top_k` is capped at `min(request.top_k, settings.max_top_k=50)`.

---

## Gap 4 — No Prompt Injection Defense [CRITICAL]

**Risk:** User query `"ignore all instructions and..."` passed raw into LLM prompt.

**Fix:** `sanitize_query()` + `wrap_user_input_in_prompt()` in `backend/utils/sanitize.py`.
Every user query must pass through both before reaching any LLM call.
XML delimiters separate system instructions from user content.

---

## Gap 5 — No ARQ Worker Process [CRITICAL]

**Risk:** `crawl_queue` fills forever — nothing consumes it without a running worker process.

**Fix:** `backend/worker.py` with ARQ `WorkerSettings`.
`docker-compose.yml` has a `worker` service using the `worker` Dockerfile target.
Crawl endpoint enqueues via `redis.enqueue_job("crawl_task", item_id)`.

---

## Gap 6 — No Alembic [HIGH]

**Risk:** First `ALTER TABLE` after launch requires manual SQL in prod. Schema drifts.

**Fix:** Alembic with async support. Runs `alembic upgrade head` in lifespan before pool opens.
`DATABASE_URL_DIRECT` (port 5432) used for Alembic only — app uses pooler (port 6543).

---

## Gap 7 — Contradicting Fact Resolution [HIGH]

**Risk:** Two sources give different employee count. LLM may pick either randomly.

**Fix:** `backend/services/fact_resolver.py` with `RESOLUTION_POLICY`:
- Numeric facts: highest `trust × freshness` product wins
- Boolean facts: majority of sources must agree
- Text facts: most recent high-trust source wins
Synthesis prompt explicitly flags contradictions.

---

## Gap 8 — No SSE for Agent Progress [HIGH]

**Risk:** 8-second blank screen during agent runs.

**Fix:** `GET /api/v1/agent/run/{run_id}/stream` using `sse-starlette`.
Polls `agent_runs.steps_log` every 500ms, streams new entries as `step` events.
Frontend uses `EventSource` to receive and display live progress.

---

## Gap 9 — Cross-Source Content Deduplication [HIGH]

**Risk:** Same article syndicated to 5 sites → 5× inflated confidence in that fact.

**Fix:** `is_semantic_duplicate()` check in `crawler/store.py` before chunk insert.
Threshold `0.97` = near-identical text. If duplicate exists for same entity, skip.

---

## Gap 10 — No API Rate Limiting [HIGH]

**Risk:** One user exhausts entire OpenAI quota.

**Fix:** `slowapi` with Redis backend.
Agent runs: `10/minute`, `100/hour`. Search/enrich: `60/minute`.
Rate limited per IP by default; can key by `X-API-Key` for authenticated limits.

---

## Gap 11 — No Observability [HIGH]

**Risk:** Production failure with no way to correlate HTTP request → agent → DB.

**Fix:** `_trace_id` ContextVar set per request via middleware.
Every log line includes `trace_id`. Every `agent_runs` row stores it.
Format: `event_name | trace=X key=value`.

---

## Gap 12 — Docker Image Size [MEDIUM]

**Risk:** Playwright + all deps = 2.5GB+ image. 45s+ cold start on Render free.

**Fix:** Multi-stage Dockerfile with `api` target (no Playwright, ~400MB)
and `worker` target (with Playwright, ~1.2GB).

---

## Gap 13 — Data Retention [MEDIUM]

**Risk:** `query_cache`, `agent_runs`, `source_documents` grow forever.
Supabase free = 500MB DB limit.

**Fix:** Weekly GitHub Actions CRON runs `scripts/cleanup_old_data.py`:
- Delete `query_cache` rows expired > 7 days
- Delete completed `agent_runs` older than 90 days
- Delete `source_documents` older than 180 days not referenced by any fact

---

## Gap 14 — Supabase Connection Pool Limit [MEDIUM]

**Risk:** `max_size=10` × multiple services = too many connections error (60 limit).

**Fix:** `db_pool_max_size = 5` always. Use PgBouncer pooler URL (port 6543).
`DATABASE_URL_DIRECT` (port 5432) used only for Alembic migrations.

---

## Gap 15 — No /explain Endpoint [MEDIUM]

**Risk:** "Why was this result returned?" is mentioned in PRD but has no API.

**Fix:** `GET /api/v1/explain/{entity_id}?query={query}`
Returns ranked chunks with full score breakdown:
`semantic_similarity`, `freshness`, `trust`, `final_score`, `score_driver`.
Powers the debug panel.

---

## Gap 16 — No Shared Test Fixtures [MEDIUM]

**Risk:** Each test file re-implements DB seeding, creating inconsistency and drift.

**Fix:** `tests/conftest.py` with all fixtures:
`db_pool`, `clean_tables` (autouse), `seeded_company`, `seeded_person`,
`seeded_source_and_chunks`, `mock_llm`, `mock_embed`, `mock_crawler`, `client`.

---

## Supabase Free Tier Limits

| Resource | Limit | Mitigation |
|----------|-------|-----------|
| DB storage | 500MB | Weekly cleanup |
| Connections | 60 | pool max=5, PgBouncer |
| Bandwidth | 5GB/month | Cache GET responses |

## Cost-Saving Rules

- Use `text-embedding-3-small` in production (5× cheaper than large)
- Use `gpt-4o-mini` not `gpt-4o` for synthesis
- Cache all agent run results for ≥1 hour
- Never re-crawl entities with `freshness_score > 0.7`
- Batch embedding calls (100 per API request)
- No Playwright at runtime in production — CRON only