---
description: Load when working on the Next.js frontend, signal extraction, Playwright crawler, remaining API routes, query cache, batch enrichment, deployment configuration, GitHub Actions, or demo/polish tasks.
applyTo: "{frontend/**,backend/routers/{search,enrich,entities,accounts,contacts,signals}.py,backend/services/signal_extractor.py,backend/services/query_cache.py,.github/workflows/**,render.yaml,scripts/**}"
---

# Phase 4 — Frontend, Signals, Playwright, Polish + Deployment

## Goal
Full working UI, all API routes complete, live demo-ready seed data,
Playwright dynamic crawler, query cache, and deployed on free-tier cloud.

## Checklist
- [ ] 4.1 Signal extractor
- [ ] 4.2 Playwright support in crawler
- [ ] 4.3 Next.js frontend (search, results, account brief, agent runner)
- [ ] 4.4 Remaining API routes (search, entities, signals, contacts, accounts)
- [ ] 4.5 Query result cache
- [ ] 4.6 Batch enrich endpoint (async job pattern)
- [ ] 4.7 Deployment config (render.yaml, vercel.json, GitHub Actions)
- [ ] 4.8 Demo debug panel + seed data
- [ ] 4.9 Integration tests
- [ ] 4.10 README + pre-demo checklist

## Step-by-Step Copilot Prompts

### 4.1 — Signal extractor
```
@workspace Implement backend/services/signal_extractor.py:
async extract_signals(clean_text, entity_id, entity_type, source_url) → List[dict]

LLM prompt (structured):
  "Read this text and identify any business signals present.
   For each signal return: signal_type (one of: hiring/funding/leadership_change/
   product_launch/website_change/expansion/layoff/acquisition/other),
   description (1 sentence), confidence (0-1), event_date (YYYY-MM-DD or null).
   Return JSON array only."

After extract_signals(), caller should upsert results to signals table.
Integrate into queue_worker.process_crawl_item() — call after storing the document.
Compute impact_score = confidence × SOURCE_TYPE_AUTHORITY[source_type].
```

### 4.2 — Playwright support
```
#file:.agents/skills/web-crawler/SKILL.md
@workspace Add Playwright to backend/crawler/fetcher.py:
- Implement _fetch_with_playwright(url, timeout_ms) using async_playwright()
  browser = chromium.launch(headless=True)
  wait_until="networkidle"
- Add auto-detect logic in fetch_page():
  After httpx fetch, if len(extract_clean_text(raw_html)) < 500 chars,
  automatically re-fetch with Playwright (JS-heavy page detected)
- Add CRAWL_USE_BROWSER_DOMAINS env var (comma-separated domain list)
  Force Playwright for these domains even if text length is sufficient
- Install Playwright browsers in Dockerfile: RUN playwright install chromium
```

### 4.3 — Next.js frontend
```
@workspace In frontend/, create a Next.js 14 App Router application with Tailwind CSS:

app/page.tsx — Home page
  Large search bar (query input), submit button
  Suggested queries: "Find engineers at...", "Account brief for...", "Hiring signals at..."
  On submit: navigate to /search?q={query}

app/search/page.tsx — Search results
  Fetch GET /api/v1/search?q={query}
  Show EntityCard components for each result
  Show confidence badge and match_type label

app/account/[id]/page.tsx — Account brief
  Fetch GET /api/v1/account/{id}/brief via agent run
  Show SignalTimeline, KeyPeople list, CitationBadge per fact

app/agent/page.tsx — Agent runner UI
  Dropdown to select workflow_name
  Textarea for query
  Submit → POST /api/v1/agent/run
  Show steps_log as live-updating list
  Show final_response as formatted JSON card

components/EntityCard.tsx — canonical entity card with name, domain, confidence
components/CitationBadge.tsx — source URL chip showing domain + fetched_at + trust score
components/SignalTimeline.tsx — vertical timeline of signals with type icon + description
components/DebugPanel.tsx — collapsible panel showing steps_log + chunk scores (shown when ?debug=true)
components/PersonCard.tsx — name, title, seniority badge, source citations

All fetch calls use NEXT_PUBLIC_API_BASE_URL env var.
Show loading skeletons during fetch. Show error state if API returns non-200.
```

### 4.4 — Remaining API routes
```
@workspace Implement these routers:

backend/routers/search.py — POST /api/v1/search
  Body: {query: str, entity_type?: str, filters?: dict}
  1. Run entity_resolver with input query
  2. Return top 5 candidates with canonical_id, canonical_name, confidence, match_type, domain
  3. Also run vector_search on query for relevant context chunks
  4. Return {candidates: [...], context_preview: first 3 ranked chunks}

backend/routers/entities.py — GET /api/v1/entity/{canonical_id}
  SELECT company or person by canonical_id
  Fetch associated facts[], signals[], people[] (if company), roles[] (if person)
  Attach citations from source_documents
  Return full canonical response shape

backend/routers/signals.py — GET /api/v1/signals/{entity_id}
  Query params: signal_type?, days_back=90, limit=20
  SELECT from signals WHERE entity_id=$1 AND detected_at > NOW() - INTERVAL '$2 days'
  ORDER BY detected_at DESC, impact_score DESC

backend/routers/contacts.py — GET /api/v1/contact/{canonical_id}
  SELECT person with roles history (JOIN roles ORDER BY start_date DESC)
  Attach source_documents as citations
  Return CitedPerson shape

backend/routers/accounts.py — GET /api/v1/account/{id}/brief
  Run account_brief agent workflow for this entity_id
  Return AgentRunResponse
```

### 4.5 — Query cache
```
@workspace Implement backend/services/query_cache.py:
- make_query_hash(query, workflow_name) → str  (SHA-256 of query+workflow)
- async get_cached(query_hash, db) → dict | None
  SELECT from query_cache WHERE query_hash=$1 AND expires_at > NOW()
  Increment hit_count on cache hit
- async set_cached(query_hash, query_text, workflow_name, response, ttl_seconds, db)
  INSERT INTO query_cache ON CONFLICT (query_hash) DO UPDATE
  Set expires_at = NOW() + INTERVAL '{ttl_seconds} seconds'

Integrate into agents/router.py run_agent():
  Before invoke: check_cache → return cached if HIT
  After invoke: set_cache with settings.cache_ttl_seconds
  Add cache_hit: bool field to AgentRunResponse
```

### 4.6 — Batch enrich endpoint
```
@workspace Implement backend/routers/enrich.py:
POST /api/v1/enrich
  Body: {name?: str, domain?: str, title?: str}
  Run entity resolution → single enrichment via crm_enrichment agent (batch_size=1)
  Return enriched entity card synchronously

POST /api/v1/enrich/batch
  Body: {leads: List[dict]}  max 500 rows
  1. Validate: each lead must have name or domain
  2. Generate job_id (UUID), INSERT into agent_runs with status=running
  3. Launch background task: run crm_enrichment agent with full lead_list
  4. Return immediately: {job_id, status:"processing", total_leads: N}

GET /api/v1/enrich/batch/{job_id}
  SELECT agent_runs by run_id
  If completed: return full output with enriched rows
  If running: return {job_id, status:"processing", progress_hint: "..."}
  If failed: return {job_id, status:"failed", error: "..."}
```

### 4.7 — Deployment config
```
#file:.agents/skills/deployment-pipeline/SKILL.md
@workspace Create all deployment files:

render.yaml — web service: python, uvicorn main:app, healthCheckPath=/api/v1/health,
  envVars: DATABASE_URL (from DB), OPENAI_API_KEY, API_KEY, LOG_LEVEL=WARNING,
  RESPECT_ROBOTS_TXT=true, CACHE_TTL_SECONDS=3600

frontend/vercel.json — framework nextjs, env vars via Vercel secrets,
  Cache-Control header s-maxage=60 stale-while-revalidate=300 on /api routes

.github/workflows/ci.yml — trigger on push/PR
  Services: pgvector/pgvector:pg16
  Steps: checkout, python 3.11, pip install, init schema, pytest tests/ -v

.github/workflows/batch_ingest.yml — trigger: schedule 0 2 * * *, workflow_dispatch
  Steps: checkout, python 3.11, pip install,
  run scripts/batch_ingest.py --stale-only --max-entities 200,
  run scripts/refresh_scores.py --threshold-days 7

scripts/batch_ingest.py — full implementation per deployment-pipeline skill
scripts/refresh_scores.py — call batch_refresh_stale_scores()
.env.example — all env vars listed with placeholder values, never real secrets
```

### 4.8 — Debug panel + demo seed data
```
@workspace Implement:

scripts/seed_demo_data.py:
  Insert 5 companies (tech companies, varied industries)
  Insert 20 people across those companies (varied titles and seniority)
  Insert 10 signals (mix of hiring, funding, product_launch)
  Insert source_documents and chunks for each company with mock embeddings
  Print summary of inserted records

frontend/components/DebugPanel.tsx:
  Only visible when URL has ?debug=true param
  Sections:
  - "Agent Steps" — expandable list from steps_log, each step as collapsible row
  - "Retrieved Chunks" — table: rank, source_url, similarity, freshness, trust, final_score
  - "Cache" — HIT/MISS badge + query_hash
  - "Timing" — duration_ms bar
  Style with Tailwind, collapse by default, expand on click
```

### 4.9 — Integration tests
```
@workspace Create tests/test_integration.py:
All tests use seed_demo_data() fixture (inserts + cleans up).
Mock all external HTTP (crawler, LLM) — test the full pipeline internally.

- test_full_lead_finder:
    query "Find engineers at {seeded_company}"
    assert response.people is non-empty
    assert all people have ≥1 citation with non-empty url
    assert response.confidence > 0.5

- test_full_account_brief:
    query account brief for seeded company id
    assert signal_timeline has entries
    assert summary is non-empty string

- test_crawl_to_retrieval:
    mock fetch_page to return fake HTML
    POST /api/v1/crawl with entity_id
    Wait for worker to process (or call process_crawl_item directly)
    Run vector_search → assert chunk from that URL in top 5 results

- test_cache_hit:
    Run same agent query twice
    Second response has cache_hit=True
    Second response duration_ms significantly less than first

- test_batch_enrichment:
    POST /api/v1/enrich/batch with 5 seeded leads
    Poll GET /api/v1/enrich/batch/{job_id} until status=completed
    Assert 5 enriched rows, each with canonical_id and ≥1 citation
```

### 4.10 — README + pre-demo checklist
```
@workspace Create README.md with these sections:
1. One-paragraph project summary (entity resolution, RAG, citations, agents)
2. Architecture overview — reference agent_graph.md, link to /docs swagger
3. Quick start:
   docker compose up -d
   cp .env.example .env
   python scripts/init_db.py
   python scripts/seed_demo_data.py
   uvicorn backend.main:app --reload
   cd frontend && npm install && npm run dev
4. Demo queries (copy-paste ready):
   "Find senior engineers at Example Inc"
   "Show recent hiring signals for Example Inc"
   "Account brief for Example Inc"
   "Why is the record for example.com stale?"
5. API reference — http://localhost:8000/docs
6. Deployment (Vercel + Render + Supabase) — 3 bullet steps each
7. Resume bullets (copy from PRD_Architecture.md section 9)
```

## Deployment Cost Rules (Enforce These)

- No Playwright on every request in production — only in GitHub Actions CRON
- Cache all agent run results in `query_cache` with at least 1-hour TTL
- `embed_batch` must use batches of 100 — never loop with individual embed() calls
- Refresh only entities with `freshness_score < 0.4` — never re-crawl healthy entities
- Use `text-embedding-3-small` in production (OpenAI) — never `text-embedding-3-large`
- Store precomputed summaries per entity — don't re-run account_brief on every page load

## Definition of Done

`scripts/seed_demo_data.py` runs without errors.
Frontend at `localhost:3000` → type "Find engineers at Example Inc" → see people results with source citations.
`POST /api/v1/enrich/batch` with 5 leads → `GET .../batch/{job_id}` returns enriched rows.
`pytest tests/test_integration.py` passes.
App deploys: Vercel frontend live, Render backend live, Supabase as DB.