---
description: Load when adding logging, trace IDs, request timing, health checks, or the /explain endpoint. Auto-loads for middleware/trace.py, routers/health.py.
applyTo: "{backend/middleware/trace.py,backend/routers/health.py,backend/main.py,backend/agents/**}"
---

# Observability — Quick Reference

Full patterns in: `#file:.agents/skills/observability-logging/SKILL.md`

## The One Rule

Every log line includes `trace_id`. Always.

```python
from backend.middleware.trace import get_trace_id
logger.info(f"my_event | trace={get_trace_id()} key=value")
```

## Log Format

```
event_name | trace=X key=value key=value
```

## Inside Every LangGraph Node

```python
async def my_node(state):
    trace = get_trace_id()
    t = time.perf_counter()
    # ... work ...
    ms = int((time.perf_counter() - t) * 1000)
    logger.info(f"node_complete | trace={trace} node=my_node ms={ms}")
    return {"steps_log": state["steps_log"] + [f"[my_node] done {ms}ms"]}
```

## Trace Middleware Import

```python
# backend/main.py
from backend.middleware.trace import trace_timing_middleware
app.middleware("http")(trace_timing_middleware)
```