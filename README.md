# CRMind

CRMind is an entity-first, citation-aware CRM intelligence platform. It resolves companies and people to canonical records, retrieves source-backed evidence using hybrid search, runs workflow agents for lead finding and account briefs, and returns structured JSON where claims include citations.

## Architecture Overview

- Backend: FastAPI + asyncpg + pgvector
- Agents: LangGraph-compatible workflow runtime with grounded retrieval
- Data: PostgreSQL (companies, people, signals, chunks, agent_runs)
- Frontend: Next.js 14 App Router under frontend
- API docs: http://localhost:8000/docs

## Quick Start

```bash
docker compose up -d
cp .env.example .env
python scripts/init_db.py
python scripts/seed_demo_data.py
uvicorn backend.main:app --reload
cd frontend && npm install && npm run dev
```

## Demo Queries

- Find senior engineers at Example Inc
- Show recent hiring signals for Example Inc
- Account brief for Example Inc
- Why is the record for example.com stale?

## API Reference

OpenAPI docs are available at:

- http://localhost:8000/docs

## Deployment

### Vercel (frontend)

1. Import only the [frontend](frontend) directory as a Vercel project.
2. Set these Vercel environment variables:
	- `NEXT_PUBLIC_API_BASE_URL=https://<your-render-service>.onrender.com/api/v1`
	- `NEXT_PUBLIC_SUPABASE_URL=https://<your-project>.supabase.co`
	- `NEXT_PUBLIC_SUPABASE_ANON_KEY=<supabase-anon-key>`
3. Keep [frontend/vercel.json](frontend/vercel.json) as-is for cache headers.
4. Deploy with the Vercel Hobby (free) tier.

### Render (backend)

1. Create a Render Web Service from [render.yaml](render.yaml) (Starter free tier).
2. Set required env vars in Render:
	- `DATABASE_URL` and `DATABASE_URL_DIRECT` (Supabase pooled/direct URLs)
	- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
	- `OPENAI_API_KEY`, `GROQ_API_KEY`, `API_KEY`, `INTERNAL_SERVICE_API_KEY`
	- `DB_POOL_MAX_SIZE=5` (important for Supabase free connection limits)
3. Confirm health endpoint at `/api/v1/health`.
4. Keep free-tier usage low by using scheduled ingest and query caching.

### Supabase (database)

1. Create a Supabase free project.
2. Enable required extensions in SQL editor:
	- `CREATE EXTENSION IF NOT EXISTS vector;`
	- `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
3. Run migrations with Alembic or `python scripts/init_db.py`.
4. Use Supabase pooled connection for `DATABASE_URL` and direct connection for `DATABASE_URL_DIRECT`.

## Free-Cost Deployment Path

1. Host frontend on Vercel Hobby.
2. Host backend API on Render free tier.
3. Use Supabase free Postgres + Auth.
4. Keep `DB_POOL_MAX_SIZE=5` and use cached agent responses (`CACHE_TTL_SECONDS=3600`) to stay in free limits.
5. Use GitHub Actions schedules for batch ingest and score refresh during off-hours.

## Resume Bullets

- Built entity-first CRM intelligence platform with grounded RAG and citation-backed responses.
- Implemented async ingestion and hybrid retrieval pipeline (vector + keyword + ranking).
- Designed multi-workflow agent system (lead finder, account brief, enrichment, research, ops debug).
- Added cache-aware agent orchestration and background crawl processing for cost efficiency.
