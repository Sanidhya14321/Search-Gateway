---
name: async-worker-sse
description: >
  Implement the ARQ background worker process for crawl queue processing, Server-Sent
  Events for streaming agent progress, multi-stage Docker builds, and the worker
  Docker Compose service. Use when the crawl queue needs a consumer, when adding
  real-time agent progress to the frontend, or when optimising the Docker image size.
  Keywords: ARQ, worker, background job, crawl queue, SSE, Server-Sent Events,
  agent streaming, Docker multi-stage, worker process, EventSource.
---

## Why This Matters

Two things break silently without this skill:
1. `POST /api/v1/crawl` inserts to `crawl_queue` but **nothing processes it**
   unless a worker process is running.
2. Agent runs take 5–8s and the frontend shows a blank screen without SSE.

---

## ARQ Worker (backend/worker.py)

```python
import asyncio, asyncpg, uuid
from arq import cron
from arq.connections import RedisSettings
from loguru import logger
from backend.config import settings
from backend.services.embedding_service import EmbeddingService
from backend.crawler.queue_worker import process_crawl_item_by_id
from backend.scoring.batch_refresh import batch_refresh_stale_scores
from backend.middleware.trace import _trace_id

async def startup(ctx):
    ctx['db_pool'] = await asyncpg.create_pool(
        settings.database_url, min_size=1, max_size=5)
    ctx['embed_service'] = embedding_service
    logger.info("worker_start | pool=ready")

async def shutdown(ctx):
    await ctx['db_pool'].close()

async def crawl_task(ctx, crawl_item_id: str):
    _trace_id.set(str(uuid.uuid4())[:8])
    async with ctx['db_pool'].acquire() as db:
        await process_crawl_item_by_id(db, ctx['embed_service'], crawl_item_id)

async def refresh_scores_task(ctx):
    async with ctx['db_pool'].acquire() as db:
        await batch_refresh_stale_scores(db, threshold_days=7)

async def cleanup_task(ctx):
    async with ctx['db_pool'].acquire() as db:
        await db.execute(
            "DELETE FROM query_cache WHERE expires_at < NOW() - INTERVAL '7 days'")
        await db.execute(
            "DELETE FROM agent_runs WHERE created_at < NOW()-INTERVAL '90 days' "
            "AND status='completed'")

class WorkerSettings:
    functions = [crawl_task]
    cron_jobs = [
        cron(refresh_scores_task, hour=2, minute=0),
        cron(cleanup_task, weekday=0, hour=3, minute=0),
    ]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 5
    job_timeout = 120
    keep_result = 300
    on_startup = startup
    on_shutdown = shutdown
    health_check_interval = 30
```

Run: `python -m arq backend.worker.WorkerSettings`

---

## Enqueue From API

```python
# backend/routers/crawl.py
from arq.connections import create_pool as redis_pool, RedisSettings

@router.post("/crawl")
async def queue_crawl(request: CrawlRequest, db=Depends(get_db)):
    item_id = await db.fetchval("""
        INSERT INTO crawl_queue (url, domain, entity_id, entity_type, priority)
        VALUES ($1,$2,$3,$4,$5) RETURNING id
    """, request.url, extract_domain(request.url),
        request.entity_id, request.entity_type, request.priority)

    redis = await redis_pool(RedisSettings.from_dsn(settings.redis_url))
    await redis.enqueue_job("crawl_task", str(item_id))
    await redis.aclose()
    return {"status": "queued", "crawl_id": str(item_id)}
```

---

## SSE — Agent Progress Streaming

```python
# backend/routers/agents.py
from sse_starlette.sse import EventSourceResponse
import json, asyncio

@router.get("/agent/run/{run_id}/stream")
async def stream_agent_run(run_id: str, db=Depends(get_db), _=Depends(verify_api_key)):
    async def generator():
        last = 0
        for _ in range(60):   # 30s max (60 × 0.5s)
            run = await db.fetchrow(
                "SELECT status, steps_log, output_payload, error_message "
                "FROM agent_runs WHERE run_id=$1", run_id)
            if not run:
                yield {"event": "error", "data": json.dumps({"error": "not found"})}
                return
            steps = run["steps_log"] or []
            for step in steps[last:]:
                yield {"event": "step", "data": json.dumps({"step": step, "index": last})}
                last = len(steps)
            if run["status"] == "completed":
                yield {"event": "done", "data": json.dumps(
                    {"status": "completed", "result": run["output_payload"]})}
                return
            if run["status"] == "failed":
                yield {"event": "done", "data": json.dumps(
                    {"status": "failed", "error": run["error_message"]})}
                return
            await asyncio.sleep(0.5)
        yield {"event": "timeout", "data": json.dumps({"error": "timed out"})}

    return EventSourceResponse(generator())
```

**Frontend EventSource pattern:**
```typescript
const url = `/api/v1/agent/run/${runId}/stream?api_key=${encodeURIComponent(apiKey)}`;
const source = new EventSource(url);
source.addEventListener("step", e => setSteps(s => [...s, JSON.parse(e.data).step]));
source.addEventListener("done", e => { setResult(JSON.parse(e.data).result); source.close(); });
```

---

## Multi-Stage Dockerfile

```dockerfile
FROM python:3.11-slim AS deps
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS api
WORKDIR /app
COPY --from=deps /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim AS worker
WORKDIR /app
COPY --from=deps /root/.local /root/.local
RUN /root/.local/bin/playwright install chromium --with-deps
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "arq", "backend.worker.WorkerSettings"]
```

**docker-compose.yml worker service:**
```yaml
worker:
  build: {context: ./backend, dockerfile: Dockerfile, target: worker}
  command: python -m arq backend.worker.WorkerSettings
  depends_on:
    postgres: {condition: service_healthy}
    redis: {condition: service_healthy}
  env_file: .env
  deploy:
    restart_policy: {condition: on-failure, max_attempts: 5}
```

---

## File Locations

```
backend/worker.py              ← ARQ WorkerSettings + all task functions
backend/routers/agents.py      ← SSE /stream endpoint
backend/routers/crawl.py       ← enqueue to ARQ on POST /crawl
Dockerfile                     ← multi-stage: api + worker
docker-compose.yml             ← worker service added
```