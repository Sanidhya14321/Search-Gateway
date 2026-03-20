---
name: observability-logging
description: >
  Add trace IDs, structured logging, request timing, circuit breaker state,
  and the /explain endpoint to CRMind. Use when adding any logging, tracing,
  metrics, health checks, or the debug panel API. Keywords: trace ID, structured
  logging, loguru, request timing, observability, X-Trace-ID, middleware,
  health endpoint, explain endpoint, log correlation.
---

## Rule: Every Log Line Must Be Correlatable

Every log line must include `trace_id`. This lets you follow one request from
HTTP entry → agent steps → DB queries in production without guessing.

---

## Trace Middleware

```python
# backend/middleware/trace.py
import uuid, time
from contextvars import ContextVar
from fastapi import Request
from loguru import logger

_trace_id: ContextVar[str] = ContextVar('trace_id', default='unknown')

def get_trace_id() -> str:
    return _trace_id.get()

async def trace_timing_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())[:8]
    _trace_id.set(trace_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
        ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            f"http_request | trace={trace_id} method={request.method} "
            f"path={request.url.path} status={response.status_code} ms={ms}"
        )
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time"] = str(ms)
        return response
    except Exception as e:
        ms = int((time.perf_counter() - start) * 1000)
        logger.error(
            f"http_error | trace={trace_id} path={request.url.path} "
            f"error={type(e).__name__} ms={ms}"
        )
        raise
```

Register: `app.middleware("http")(trace_timing_middleware)`

---

## Loguru Setup

```python
# backend/main.py
from loguru import logger
import sys

def configure_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level=settings.log_level,
        colorize=(settings.environment == "local"),
        serialize=(settings.log_format == "json"),
    )
```

---

## Log Format

All lines: `event_name | key=value key=value`

```
http_request  | trace=a1b2c3 method=POST path=/api/v1/agent/run status=200 ms=1243
agent_start   | trace=a1b2c3 run_id=run_xyz workflow=lead_finder
node_complete | trace=a1b2c3 node=resolve_company ms=45 confidence=0.94
vector_search | trace=a1b2c3 entity_id=comp_abc results=18 ms=32
llm_call      | trace=a1b2c3 model=llama3 tokens_in=1200 ms=3400
llm_degraded  | trace=a1b2c3 reason=circuit_open fallback=template
crawl_done    | url=https://acme.com status=200 chunks=24 ms=890
crawl_skip    | url=https://acme.com reason=content_unchanged
```

---

## Logging Inside Nodes

```python
async def some_node(state: CRMindState) -> dict:
    trace = get_trace_id()
    t = time.perf_counter()
    # ... work ...
    ms = int((time.perf_counter() - t) * 1000)
    logger.info(f"node_complete | trace={trace} node=some_node ms={ms}")
    return {
        "steps_log": state["steps_log"] + [f"[some_node] done in {ms}ms"],
    }
```

---

## /explain Endpoint

Powers the debug panel. Returns full score breakdown for any query+entity.

```python
# backend/routers/entities.py
@router.get("/explain/{entity_id}")
async def explain_results(entity_id: str, query: str,
                          db=Depends(get_db),
                          embed_service=Depends(get_embed_service)):
    chunks = await vector_search(query, entity_id=entity_id, top_k=10, db=db)
    chunks = rank_chunks(chunks)
    return {
        "query": query, "entity_id": entity_id,
        "explanation": [
            {
                "rank": i + 1,
                "source_url": c.source_url,
                "excerpt": c.chunk_text[:200],
                "scores": {
                    "semantic_similarity": round(c.similarity, 3),
                    "freshness":           round(c.freshness_score, 3),
                    "trust":               round(c.trust_score, 3),
                    "final_score":         round(c.final_score, 3),
                },
                "score_driver": max(
                    {"semantic": c.similarity * 0.4,
                     "freshness": c.freshness_score * 0.25,
                     "trust": c.trust_score * 0.2},
                    key=lambda k, c=c: {
                        "semantic": c.similarity * 0.4,
                        "freshness": c.freshness_score * 0.25,
                        "trust": c.trust_score * 0.2
                    }[k]
                ),
            }
            for i, c in enumerate(chunks)
        ]
    }
```

---

## Enhanced Health Endpoint

```python
@router.get("/health")
async def health(db=Depends(get_db)):
    checks = {}
    try:
        await db.fetchval("SELECT 1"); checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"error:{type(e).__name__}"
    checks["llm_circuit"]   = llm_breaker._state.value
    checks["embed_circuit"] = embed_breaker._state.value
    overall = "ok" if all(v == "ok" for v in checks.values()
                          if "circuit" not in k
                          for k in [list(checks.keys())[list(checks.values()).index(v)]]
                          ) else "degraded"
    return JSONResponse(
        status_code=200 if overall == "ok" else 503,
        content={"status": overall, "checks": checks,
                 "version": "1.0.0",
                 "timestamp": datetime.now(timezone.utc).isoformat()}
    )
```

---

## File Locations

```
backend/middleware/trace.py     ← _trace_id, get_trace_id, trace_timing_middleware
backend/routers/health.py       ← enhanced health with circuit breaker states
backend/routers/entities.py     ← /explain/{entity_id} endpoint
```