---
description: Load when modifying the database schema, creating Alembic migrations, adding columns or tables, upgrading the embedding model, or configuring Supabase connection pooling.
applyTo: "{alembic/**,alembic.ini,scripts/rembed_chunks.py,backend/database.py,backend/services/retrieval/vector_search.py}"
---

# Database Migrations — Quick Reference

Full patterns in: `#file:.agents/skills/db-migrations-embedding-versioning/SKILL.md`

## Schema Change Checklist

1. `alembic revision -m "describe_change"` — generate file
2. Write `upgrade()` and `downgrade()` in the new file
3. Test locally: `alembic upgrade head`
4. Commit the revision file
5. Never run raw ALTER in production

## Embedding Model Filter (CRITICAL)

Every vector search query MUST include this filter:
```python
WHERE c.embed_model_id = $1   # settings.embedding_model
```
Omitting this causes silent wrong results when models differ.

## Supabase Pool Config

```python
# ALWAYS these values for Supabase free tier
db_pool_max_size = 5        # hard cap — 60 connection limit on free tier
DATABASE_URL = "...port=6543...?pgbouncer=true"   # pooler, NOT port 5432
DATABASE_URL_DIRECT = "...port=5432..."            # Alembic only
```

## Model Upgrade Procedure

```bash
# 1. Dry run first
python scripts/rembed_chunks.py --model text-embedding-3-small --dry-run
# 2. Re-embed
python scripts/rembed_chunks.py --model text-embedding-3-small
# 3. Verify: SELECT embed_model_id, COUNT(*) FROM chunks GROUP BY 1
# 4. Update settings.embedding_model, deploy
```