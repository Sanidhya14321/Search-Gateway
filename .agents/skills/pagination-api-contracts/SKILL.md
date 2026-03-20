---
name: pagination-api-contracts
description: >
  Add pagination to all list endpoints, implement the PaginatedResponse generic,
  ETag caching, idempotency keys for batch enrich, OpenAPI tags, rate limiting
  with slowapi, and the required fields checklist for every API response.
  Use when creating or modifying any endpoint that returns a list, when adding
  rate limiting, or when validating response shapes. Keywords: pagination,
  PaginatedResponse, limit offset, total, has_more, ETag, rate limit, slowapi,
  idempotency, OpenAPI, response contract.
---

## Rule: Every List Endpoint Must Be Paginated

Any endpoint returning more than one item must support `limit`/`offset`
and return `total`/`has_more`. No exceptions.

---

## PaginatedResponse Generic

```python
# backend/models/responses.py
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
import base64, json

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool
    next_cursor: Optional[str] = None

    @classmethod
    def build(cls, items, total, limit, offset):
        has_more = (offset + len(items)) < total
        cursor = None
        if has_more and items:
            cursor = base64.b64encode(
                json.dumps({"offset": offset + limit}).encode()
            ).decode()
        return cls(items=items, total=total, limit=limit,
                   offset=offset, has_more=has_more, next_cursor=cursor)
```

---

## Pagination Params

```python
# backend/models/requests.py
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
```

Usage: `pagination: PaginationParams = Depends()`

---

## Paginated Endpoint Pattern

```python
@router.get("/signals/{entity_id}", response_model=PaginatedResponse[SignalResult])
async def get_signals(entity_id: str, pagination: PaginationParams = Depends(),
                      db=Depends(get_db)):
    total = await db.fetchval(
        "SELECT COUNT(*) FROM signals WHERE entity_id=$1", entity_id)
    rows = await db.fetch("""
        SELECT * FROM signals WHERE entity_id=$1
        ORDER BY detected_at DESC LIMIT $2 OFFSET $3
    """, entity_id, pagination.limit, pagination.offset)
    items = [SignalResult(**dict(r)) for r in rows]
    return PaginatedResponse.build(items, total, pagination.limit, pagination.offset)
```

---

## Rate Limiting (slowapi)

```python
# backend/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# backend/routers/agents.py
@router.post("/agent/run")
@limiter.limit("10/minute")
@limiter.limit("100/hour")
async def run_agent_endpoint(request: Request, ...): ...
```

---

## ETag Caching

```python
# backend/utils/etag.py
import hashlib, json
from fastapi import Request, Response
from fastapi.responses import JSONResponse

def make_etag(data: dict) -> str:
    return hashlib.md5(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()

# In entity router:
etag = make_etag(entity_data)
if request.headers.get("If-None-Match") == etag:
    return Response(status_code=304)
resp = JSONResponse(content=entity_data)
resp.headers["ETag"] = etag
resp.headers["Cache-Control"] = "private, max-age=300"
return resp
```

---

## Idempotency on Batch Enrich

```python
# backend/routers/enrich.py
class BatchEnrichRequest(BaseModel):
    leads: List[dict] = Field(..., min_length=1, max_length=500)
    idempotency_key: Optional[str] = None

@router.post("/enrich/batch")
async def batch_enrich(request: BatchEnrichRequest, db=Depends(get_db)):
    if request.idempotency_key:
        key_hash = hashlib.sha256(request.idempotency_key.encode()).hexdigest()
        existing = await db.fetchrow(
            "SELECT run_id, status FROM agent_runs WHERE input_hash=$1", key_hash)
        if existing:
            return {"job_id": existing["run_id"], "status": existing["status"],
                    "message": "Duplicate — returning existing job"}
```

---

## Required Fields Checklist

Every response must include:

| Field | Required | Notes |
|-------|----------|-------|
| `entity_id` | Yes | Frontend needs for follow-ups |
| `confidence` | Yes | Transparency |
| `retrieved_at` | Yes | Freshness |
| `pipeline_version` | Yes | Debug after deploys |
| `citations[].url` | Yes | Every claim needs a source |
| `citations[].fetched_at` | Yes | Evidence freshness |
| `degraded` | If applicable | Never silently degrade |
| `total` + `has_more` | On all lists | Pagination |
| `trace_id` | In error responses | Log correlation |

---

## File Locations

```
backend/models/
  requests.py    ← PaginationParams, BatchEnrichRequest (with idempotency_key)
  responses.py   ← PaginatedResponse[T], all response models
backend/utils/
  etag.py        ← make_etag()
backend/main.py  ← slowapi limiter setup
backend/routers/
  signals.py     ← paginated example
  enrich.py      ← idempotency_key
```