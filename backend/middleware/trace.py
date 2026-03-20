import time
from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request
from loguru import logger

_trace_id: ContextVar[str] = ContextVar("trace_id", default="unknown")


def get_trace_id() -> str:
    return _trace_id.get()


async def trace_timing_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID") or str(uuid4())[:8]
    token = _trace_id.set(trace_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "http_request | trace={} method={} path={} status={} ms={}",
            trace_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time"] = str(elapsed_ms)
        return response
    finally:
        _trace_id.reset(token)
