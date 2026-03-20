---
description: Load these instructions for all tasks in the CRMind project. Applies to backend Python, frontend Next.js, database, agent workflows, and deployment code.
applyTo: "**"
---

# CRMind — Project Context & Coding Guidelines

## What This Project Is

CRMind is an entity-first, citation-aware AI search and CRM intelligence system.
It resolves companies and people to canonical records, pulls multi-source evidence,
ranks by freshness and trust, and returns structured JSON responses with traceable
source citations — never freeform LLM answers from memory.

## Absolute Rules (Never Break These)

- **LLMs never answer from memory.** Every synthesis node must receive retrieved context as input.
- **Every claim in a response must have ≥1 source citation** with a URL, fetch date, and trust score.
- **Entity resolution always runs before retrieval.** Never search without a resolved `entity_id`.
- **Respect `robots.txt` by default.** Only bypass with explicit `respect_robots=False`.
- **No secrets in code.** All keys come from environment variables via `config.py`.
- **Async everywhere.** All DB, HTTP, and LLM calls must be `async/await`.
- **Never mix embedding models.** Every `chunks` row stores `embed_model_id`. Every vector search filters by it.
- **Never raise HTTP 500 when partial results exist.** Return best available with `degraded: true`.
- **Never return a list endpoint without pagination.** `limit`/`offset`/`total`/`has_more` on every list.
- **Never call real LLM or web URLs in tests.** All external calls mocked at service boundary.
- **Every log line includes `trace_id`.** Set via `X-Trace-ID` header middleware.
- **Wrap all user input in prompt delimiters.** Use `wrap_user_input_in_prompt()` before any LLM call.
- **DB pool max_size = 5 on Supabase free tier.** Never set higher (60 connection hard limit).
- **Schema changes = Alembic revision.** Never run raw ALTER in production.

## Project Stack

| Layer | Local (demo) | Deployed (free tier) |
|-------|-------------|---------------------|
| Frontend | Next.js 14 App Router | Vercel Hobby |
| Backend API | FastAPI + asyncpg | Render free |
| Database | PostgreSQL 16 + pgvector | Supabase free (PgBouncer port 6543) |
| Embeddings | OpenAI `text-embedding-3-small` | OpenAI `text-embedding-3-small` |
| LLM | Groq `llama-3.3-70b-versatile` | Groq `llama-3.3-70b-versatile` |
| Crawler | httpx (static) + Playwright (dynamic/CRON) | httpx only at runtime |
| Agents | LangGraph `StateGraph` | LangGraph `StateGraph` |
| Queue | Redis + ARQ worker process | Redis + ARQ |
| Resilience | tenacity retry + circuit breaker | same |
| Migrations | Alembic (runs on startup) | same |

## Repository Structure

```
backend/
  main.py              # FastAPI app + lifespan (runs Alembic on start)
  config.py            # pydantic-settings, all env vars
  database.py          # asyncpg pool (max_size=5)
  dependencies.py      # FastAPI Depends (db, auth, embed_service)
  worker.py            # ARQ WorkerSettings + task functions
  routers/             # one file per endpoint group
  models/
    requests.py        # Pydantic request schemas + PaginationParams
    responses.py       # PaginatedResponse[T] + all response models
  middleware/
    trace.py           # _trace_id ContextVar + trace_timing_middleware
  utils/
    retry.py           # llm_retry, db_retry (tenacity)
    circuit_breaker.py # CircuitBreaker + llm_breaker, embed_breaker singletons
    sanitize.py        # sanitize_query, wrap_user_input_in_prompt
    exceptions.py      # CRMindError hierarchy
    etag.py            # make_etag, ETag response helpers
  services/
    entity_resolver.py
    embedding_service.py  # model-versioned, stores embed_model_id
    query_cache.py
    fact_resolver.py      # contradicting fact resolution
    signal_extractor.py
    retrieval/
      vector_search.py    # MUST filter by embed_model_id
      keyword_search.py
      merger.py
      ranker.py
      context_assembler.py
    citations/
      builder.py
      finder.py
      formatter.py
      assembler.py
      validator.py
  agents/
    state.py           # CRMindState TypedDict
    router.py          # run_agent(), WORKFLOW_REGISTRY, query cache integration
    llm_client.py      # with circuit breaker + retry
    nodes/
    lead_finder.py
    account_brief.py
    crm_enrichment.py
    research.py
    ops_debug.py
  crawler/
    fetcher.py
    extractor.py
    robots.py
    rate_limiter.py
    chunker.py
    queue_worker.py    # process_crawl_item_by_id
    store.py           # semantic dedup (threshold 0.97) before chunk insert
  scoring/
    freshness.py
    trust.py
    authority.py
    signals.py
    batch_refresh.py
  tests/
alembic/
  env.py
  versions/
    001_initial_schema.py
    002_add_embed_model_id.py
    003_add_trace_id_agent_runs.py
    004_add_rate_limit.py
    005_retention_indexes.py
alembic.ini
Dockerfile             # multi-stage: deps → api (no Playwright) + worker (with Playwright)
docker-compose.yml     # 4 services: postgres, redis, api, worker
.agents/skills/        # skill files (read-only reference, do not edit)
.docs/                 # architecture docs (read-only reference)
.github/instructions/  # Copilot instruction files
frontend/
scripts/
  init_db.py
  seed_demo_data.py
  batch_ingest.py
  refresh_scores.py
  cleanup_old_data.py
  rembed_chunks.py
```

## Canonical Data Model

```
Company      → canonical_id, domain, aliases[], trust_score, freshness_score
Person       → canonical_id, full_name, seniority_level, current_company_id
Role         → person_id, company_id, title, is_current
SourceDocument → source_url, source_type, clean_text, content_hash, fetched_at
Chunk        → source_doc_id, chunk_text, embedding(768), embed_model_id, freshness_score
Fact         → entity_id, claim, confidence, source_doc_id
Signal       → entity_id, signal_type, description, confidence, detected_at
AgentRun     → run_id, workflow_name, status, steps_log, trace_id, cache_hit
```

## Ranking Formula

```python
final_score = (
    0.40 * semantic_similarity
  + 0.25 * freshness_score       # exp(-decay_rate * days_since_fetched)
  + 0.20 * trust_score           # based on source_type
  + 0.15 * source_authority      # domain-level weight
)
```

## Canonical Response Shape

Every API response must match this shape:
```json
{
  "entity_id": "comp_abc123",
  "entity_type": "company",
  "canonical_name": "Acme Corp",
  "confidence": 0.94,
  "summary": "...",
  "degraded": false,
  "facts":   [{ "claim": "...", "confidence": 0.9,
                "citations": [{ "url": "...", "fetched_at": "...",
                                "trust_score": 0.85, "freshness_score": 0.9 }] }],
  "signals": [{ "signal_type": "hiring", "description": "...", "confidence": 0.85 }],
  "people":  [{ "full_name": "...", "current_title": "...", "citations": [...] }],
  "citations": [...],
  "retrieved_at": "2024-04-01T09:00:00Z",
  "pipeline_version": "1.0.0"
}
```

## Coding Conventions

- Python 3.11+, type hints on all functions
- `async def` for all DB, HTTP, embedding, and LLM calls
- Pydantic v2 for all request/response models
- `loguru` for structured logging: `logger.info("event | key=value key=value")`
- Every log line includes `trace_id` from `middleware.trace.get_trace_id()`
- Return partial state dicts from LangGraph nodes (never mutate state in place)
- All SQL via asyncpg parameterised queries (`$1`, `$2`) — no f-string SQL
- Tests: `pytest-asyncio`, mock LLM + HTTP + embed at service boundary
- File names: `snake_case.py` — class names: `PascalCase` — constants: `UPPER_SNAKE`

## Instruction Files Reference

| Working on... | Load this |
|--------------|-----------|
| Any file | `#file:.github/instructions/Project.instructions.md` (auto) |
| DB / migrations | `#file:.github/instructions/DbMigrations.instructions.md` |
| Crawler / ingestion | `#file:.agents/skills/web-crawler/SKILL.md` |
| Retrieval / pgvector | `#file:.agents/skills/rag-retrieval-pipeline/SKILL.md` |
| Scoring | `#file:.agents/skills/trust-freshness-scoring/SKILL.md` |
| Agent graphs | `#file:.agents/skills/langgraph-agent-workflows/SKILL.md` |
| Citations | `#file:.agents/skills/citation-structured-response/SKILL.md` |
| FastAPI routes | `#file:.agents/skills/fastapi-backend-structure/SKILL.md` |
| Pagination / contracts | `#file:.github/instructions/PaginationContracts.instructions.md` |
| Error handling | `#file:.agents/skills/error-handling-resilience/SKILL.md` |
| Logging / tracing | `#file:.agents/skills/observability-logging/SKILL.md` |
| Worker / SSE / Docker | `#file:.agents/skills/async-worker-sse/SKILL.md` |
| Tests | `#file:.agents/skills/testing/SKILL.md` |
| Deployment / CI | `#file:.agents/skills/deployment-pipeline/SKILL.md` |
| Architecture questions | `#file:.docs/Architecture-Gaps.md` |

## Critical Config Values

```python
db_pool_max_size = 5          # Supabase free: 60 connection hard limit
embedding_dimensions = 768    # must match embed model; changing = re-embed all chunks
top_k_final = 8               # chunks to LLM; higher = more cost
chunk_size = 512              # changing = re-chunk + re-embed everything
cache_ttl_seconds = 3600      # increase to reduce LLM costs
crawl_min_delay_seconds = 3.0 # per domain; lower = risk of IP ban
```