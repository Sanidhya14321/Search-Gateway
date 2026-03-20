---
description: Load when working on database schema, FastAPI server setup, entity resolution, project scaffolding, or any Phase 1 foundation tasks.
applyTo: "{backend/main.py,backend/config.py,backend/database.py,backend/dependencies.py,backend/services/entity_resolver.py,backend/routers/health.py,supabase/migrations/**,scripts/init_db.py,docker-compose.yml}"
---

# Phase 1 — Foundation

## Goal
Working Postgres schema, FastAPI server, and basic entity lookup.
All subsequent phases depend on this being solid.

## Checklist
- [ ] 1.1 Project scaffold (directories + requirements.txt)
- [ ] 1.2 docker-compose.yml (postgres pgvector + redis)
- [ ] 1.3 Database schema applied (`supabase/migrations/001_initial.sql`)
- [ ] 1.4 `config.py` + `database.py`
- [ ] 1.5 `main.py` with lifespan, CORS, stub routers, global error handler
- [ ] 1.6 `entity_resolver.py`
- [ ] 1.7 `/api/v1/health` endpoint
- [ ] 1.8 Phase 1 tests passing

## Step-by-Step Copilot Prompts

### 1.1 — Project scaffold
```
@workspace Create a new Python project with this directory structure:
backend/{main.py,config.py,database.py,dependencies.py}
backend/{routers,models,services,crawler,agents,scoring,tests}/
frontend/ (empty Next.js 14 placeholder)
scripts/{batch_ingest.py,refresh_scores.py,seed_demo_data.py}
.env.example docker-compose.yml requirements.txt

Add to requirements.txt:
fastapi uvicorn[standard] asyncpg pydantic pydantic-settings
langchain langgraph playwright beautifulsoup4 lxml httpx redis arq
pgvector numpy scikit-learn loguru python-dotenv pytest pytest-asyncio
```

### 1.2 — Docker Compose
```
@workspace Create docker-compose.yml with:
- postgres service: image pgvector/pgvector:pg16, port 5432,
  env POSTGRES_DB=crmind POSTGRES_USER=dev POSTGRES_PASSWORD=dev,
  named volume for data persistence
- redis service: image redis:7-alpine, port 6379
- healthchecks on both services
```

### 1.3 — Database schema
```
#file:.docs/database-schema.md
@workspace Copy this schema into supabase/migrations/001_initial.sql.
Then create scripts/init_db.py that:
1. Reads DATABASE_URL from environment via python-dotenv
2. Connects with asyncpg
3. Executes the SQL file
4. Prints each table name as it's created
5. Prints "Schema applied successfully" on completion
```

### 1.4 — Config and database layer
```
#file:.agents/skills/fastapi-backend-structure/SKILL.md
@workspace Implement backend/config.py using pydantic-settings with these fields:
database_url, redis_url, groq_api_key, groq_llm_model, groq_llm_model_fallback,
openai_api_key, embedding_model, embedding_dimensions=1536, top_k_retrieval=20, top_k_final=8,
min_similarity=0.3, crawl_min_delay_seconds=3.0, respect_robots_txt=True,
cache_ttl_seconds=3600, log_level="INFO", api_key.
Config loads from .env file.

Then implement backend/database.py with asyncpg pool:
create_pool(), close_pool(), get_pool() — pool size min=2 max=10.
```

### 1.5 — FastAPI app
```
#file:.agents/skills/fastapi-backend-structure/SKILL.md
@workspace Implement backend/main.py with:
- FastAPI(title="CRMind API", version="1.0.0") with asynccontextmanager lifespan
  calling create_pool() on startup, close_pool() on shutdown
- CORSMiddleware allow_origins=["*"]
- Stub include_router() calls for: search, enrich, entities, accounts,
  contacts, crawl, signals, agents, health — all prefixed /api/v1
- Global exception handler returning JSON {error, detail, path}
- loguru logger configured from settings.log_level
```

### 1.6 — Entity resolver
```
#file:.agents/skills/entity-resolution/SKILL.md
@workspace Implement backend/services/entity_resolver.py following the
resolution algorithm in the skill exactly:
Step 1: exact domain match (SELECT WHERE domain = $1)
Step 2: fuzzy pg_trgm (similarity > 0.4, ORDER BY sim DESC)
Step 3: alias array match (WHERE $1 = ANY(aliases))
Step 4: embedding fallback (only if steps 1-3 return nothing)
Step 5: confidence scoring based on match_type

Return ResolvedEntity dataclass. Return None if confidence < 0.6.
Include normalize_domain() helper.
Never create new entities silently.
```

### 1.7 — Health endpoint
```
@workspace Implement backend/routers/health.py:
GET /api/v1/health
- Run SELECT 1 against DB pool; catch exception
- Return 200: {"status":"ok","db":"connected","version":"1.0.0","timestamp":"..."}
- Return 503: {"status":"degraded","db":"unreachable","error":"..."} if DB fails
Tag: ["health"], no auth required
```

### 1.8 — Phase 1 tests
```
@workspace Create tests/test_phase1.py with pytest-asyncio tests:
- test_health_ok: GET /health → 200, db=connected
- test_health_db_down: mock pool failure → 503
- test_entity_resolver_exact_domain: seed Example Inc, resolve "example.com" → confidence ≥ 0.95
- test_entity_resolver_fuzzy: resolve "Exampl Corp" → still finds Example Inc, confidence ≥ 0.6
- test_entity_resolver_not_found: resolve "zzzunknown999xyz" → returns None
- test_normalize_domain: "https://www.Acme.com/" → "acme.com"
Use pytest fixtures for DB pool. Seed the Example Inc row in conftest.py.
```

## Key Constraints for This Phase

- The `crawl_queue` table must use `FOR UPDATE SKIP LOCKED` in worker queries
- `content_hash` is SHA-256 of `clean_text` — compute before any DB write
- `canonical_id` format: `comp_{slugified_name}` — slugify = lowercase + replace spaces/punctuation with `_`
- `freshness_score` and `trust_score` default to `0.5` on insert; computed values come later in Phase 2
- Enable `pg_trgm` extension in `001_initial.sql` before creating trigram indexes

## Definition of Done

`pytest tests/test_phase1.py` passes with a live pgvector Postgres container running.
`GET /api/v1/health` returns `200` with `"db": "connected"`.
`resolve_entity("example.com")` returns a `ResolvedEntity` with `confidence ≥ 0.95`.