---
description: Load when implementing the ARQ worker process, crawl queue consumption, SSE agent streaming, Docker multi-stage builds, or the worker Docker Compose service.
applyTo: "{backend/worker.py,backend/routers/agents.py,backend/routers/crawl.py,docker-compose.yml,Dockerfile*}"
---

# Async Worker & SSE — Quick Reference

Full patterns in: `#file:.agents/skills/async-worker-sse/SKILL.md`

## Without This, Two Things Break Silently

1. `crawl_queue` fills forever — nothing consumes it
2. 8-second blank screen on agent runs — no progress stream

## Run the Worker

```bash
# Local
python -m arq backend.worker.WorkerSettings

# Docker (in docker-compose.yml)
worker:
  build: {context: ./backend, target: worker}
  command: python -m arq backend.worker.WorkerSettings
```

## Enqueue After Inserting to crawl_queue

```python
redis = await redis_pool(RedisSettings.from_dsn(settings.redis_url))
await redis.enqueue_job("crawl_task", str(item_id))
await redis.aclose()
```

## SSE Endpoint

```
GET /api/v1/agent/run/{run_id}/stream
```
Events: `step` (progress), `done` (completed/failed), `timeout`, `error`

## Docker Image Targets

- `api` target: no Playwright, ~400MB
- `worker` target: with Playwright, ~1.2GB
- Never add Playwright to the api target