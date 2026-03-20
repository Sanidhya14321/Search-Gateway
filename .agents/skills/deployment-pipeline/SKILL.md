---
name: deployment-pipeline
description: >
  Configure and manage the free-tier deployment pipeline for CRMind using Vercel,
  Supabase, Render/Cloudflare, and GitHub Actions. Use this skill when setting up
  CI/CD, batch ingestion cron jobs, environment configuration, Supabase migrations,
  Vercel deployments, caching strategies, or cost optimisation for low-resource
  hosting. Keywords: deployment, Vercel, Supabase, Render, GitHub Actions, CRON,
  batch ingestion, free tier, CI/CD, environment variables, migrations.
---

## Architecture Summary

```
User → Vercel (Next.js frontend)
          │
          ▼
     Render / Cloudflare Workers (FastAPI backend)
          │
          ▼
     Supabase (Postgres + pgvector + auth)

[GitHub Actions CRON]
  → batch_ingest.py → Supabase (embed + upsert)
```

---

## Supabase Setup

### 1. Enable pgvector

```sql
-- Run in Supabase SQL editor
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 2. Run migrations (via supabase CLI)

```bash
# Install supabase CLI
npm install -g supabase

# Init project
supabase init
supabase link --project-ref YOUR_PROJECT_REF

# Apply schema
supabase db push
# or
psql $SUPABASE_DB_URL -f database_schema.sql
```

### 3. Row Level Security (RLS)

```sql
-- Enable RLS on all user-facing tables
ALTER TABLE companies  ENABLE ROW LEVEL SECURITY;
ALTER TABLE people     ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts   ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;

-- Public read policy (adjust as needed)
CREATE POLICY "Public read companies"
  ON companies FOR SELECT USING (true);

-- Authenticated write
CREATE POLICY "Auth write companies"
  ON companies FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');
```

---

## Vercel Frontend Deployment

### vercel.json

```json
{
  "framework": "nextjs",
  "buildCommand": "next build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "@api_base_url",
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase_url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase_anon_key"
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "s-maxage=60, stale-while-revalidate=300" }
      ]
    }
  ]
}
```

### Deploy

```bash
npm install -g vercel
vercel --prod
```

---

## Render Backend Deployment

### render.yaml

```yaml
services:
  - type: web
    name: crmind-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: crmind-db   # or use Supabase URL
          property: connectionString
      - key: OLLAMA_BASE_URL
        value: ""           # leave empty; use OpenAI in production
      - key: OPENAI_API_KEY
        sync: false
      - key: API_KEY
        sync: false
    healthCheckPath: /api/v1/health
    autoDeploy: true
```

---

## GitHub Actions: Scheduled Batch Ingestion

### .github/workflows/batch_ingest.yml

```yaml
name: Batch Ingestion

on:
  schedule:
    - cron: "0 2 * * *"   # daily at 2am UTC
  workflow_dispatch:        # allow manual trigger

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run batch ingestion
        env:
          DATABASE_URL:   ${{ secrets.DATABASE_URL }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m scripts.batch_ingest --stale-only --max-entities 200

      - name: Refresh scores
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python -m scripts.refresh_scores --threshold-days 7
```

---

## GitHub Actions: CI Tests

### .github/workflows/ci.yml

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_DB: crmind_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: --health-cmd pg_isready --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: psql postgresql://test:test@localhost/crmind_test -f database_schema.sql
      - run: pytest tests/ -v --tb=short
        env:
          DATABASE_URL: postgresql://test:test@localhost/crmind_test
```

---

## Batch Ingestion Script

```python
# scripts/batch_ingest.py
import asyncio
import argparse
from database import create_pool, get_pool
from crawler.queue_worker import crawl_worker
from scoring.batch_refresh import batch_refresh_stale_scores

async def main(stale_only: bool, max_entities: int):
    await create_pool()
    pool = await get_pool()

    async with pool.acquire() as db:
        if stale_only:
            # Only queue crawls for stale entities
            stale = await db.fetch("""
                SELECT id, domain, 'company' as entity_type
                FROM companies
                WHERE freshness_score < 0.4
                  OR updated_at < NOW() - INTERVAL '7 days'
                LIMIT $1
            """, max_entities)

            for entity in stale:
                if entity["domain"]:
                    await db.execute("""
                        INSERT INTO crawl_queue (url, domain, entity_id, entity_type, priority)
                        VALUES ($1, $2, $3, $4, 3)
                        ON CONFLICT DO NOTHING
                    """,
                    f"https://{entity['domain']}",
                    entity["domain"],
                    entity["id"],
                    entity["entity_type"],
                    )

    # Run crawl workers
    await crawl_worker(pool, embed_service=None, batch_size=10)

    # Refresh scores after ingestion
    async with pool.acquire() as db:
        await batch_refresh_stale_scores(db, threshold_days=7)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stale-only", action="store_true")
    parser.add_argument("--max-entities", type=int, default=100)
    args = parser.parse_args()
    asyncio.run(main(args.stale_only, args.max_entities))
```

---

## Cost Optimisation Rules

1. **Precompute, don't recompute.** Embed at ingestion time; never at query time if avoidable.
2. **Cache repeated queries.** Use `query_cache` table with 1-hour TTL.
3. **Batch embedding calls.** Send 100 chunks per API call, not 1 at a time.
4. **No browser rendering in production** unless the URL is specifically flagged as JS-only.
5. **Use `text-embedding-3-small`** (OpenAI) in production — 5x cheaper than large.
6. **Stale-only crawling.** Don't re-crawl fresh entities; use `freshness_score` threshold.
7. **Store summaries.** Cache account brief results in `query_cache` for 24 hours.

---

## Environment Variables — Production

```bash
# Backend (Render)
DATABASE_URL=postgresql://...supabase.co/postgres
OPENAI_API_KEY=sk-...
API_KEY=your-production-api-key
LOG_LEVEL=WARNING
RESPECT_ROBOTS_TXT=true
CACHE_TTL_SECONDS=3600

# Frontend (Vercel env)
NEXT_PUBLIC_API_BASE_URL=https://crmind-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

## File locations

```
.github/
  workflows/
    ci.yml
    batch_ingest.yml
scripts/
  batch_ingest.py
  refresh_scores.py
  seed_dev_data.py
backend/
  render.yaml
frontend/
  vercel.json
supabase/
  migrations/
    001_initial_schema.sql
```