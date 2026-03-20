---
description: Load when adding pagination, rate limiting, ETag caching, idempotency keys, or validating the API response contract. Auto-loads for routers/** and models/**.
applyTo: "{backend/routers/**,backend/models/requests.py,backend/models/responses.py,backend/utils/etag.py}"
---

# Pagination & API Contracts — Quick Reference

Full patterns in: `#file:.agents/skills/pagination-api-contracts/SKILL.md`

## Every List Endpoint Needs

```python
# 1. Accept pagination params
pagination: PaginationParams = Depends()

# 2. Count before paging
total = await db.fetchval("SELECT COUNT(*) FROM table WHERE ...")

# 3. Page the query
rows = await db.fetch("SELECT ... LIMIT $N OFFSET $M", ..., pagination.limit, pagination.offset)

# 4. Return paginated response
return PaginatedResponse.build(items, total, pagination.limit, pagination.offset)
```

## Required Response Fields Checklist

- [ ] `entity_id` present
- [ ] `confidence` present
- [ ] `retrieved_at` present
- [ ] `citations[].url` non-empty for every fact/person
- [ ] `degraded` field present if LLM unavailable
- [ ] `total` + `has_more` on any list response
- [ ] `trace_id` in all error responses

## Rate Limit Decorators

```python
@limiter.limit("10/minute")   # on /agent/run
@limiter.limit("60/minute")   # on /search, /enrich
```

## Vector Search Bounds

```python
# Always cap top_k
top_k = min(request.top_k, settings.max_top_k)   # max_top_k = 50
```