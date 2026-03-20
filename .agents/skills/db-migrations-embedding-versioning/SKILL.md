---
name: db-migrations-embedding-versioning
description: >
  Manage database schema migrations with Alembic and handle embedding model
  versioning safely. Use when adding columns or tables, running ALTER statements,
  upgrading the embedding model, or configuring Supabase connection pooling.
  Keywords: Alembic, migration, ALTER TABLE, embed_model_id, embedding versioning,
  re-embed, rembed_chunks, Supabase, PgBouncer, schema change.
---

## Critical Rule: Embedding Model Versioning

Changing the embedding model (e.g. OpenAI model A -> OpenAI model B) invalidates ALL existing
vectors. Cosine similarity between vectors from different models is meaningless —
**no error, just silent wrong retrieval**. This is the most dangerous silent
failure in any RAG system.

**Fix:** Every chunk row stores the model that created it.
Every vector search filters to match the current model.

```sql
-- Already in migration 002
chunks.embed_model_id VARCHAR(64) NOT NULL DEFAULT 'text-embedding-3-small'
chunks.embed_model_version VARCHAR(32) DEFAULT '1.0'
```

```python
# vector_search.py — ALWAYS include this filter
sql = """
    SELECT ...
    FROM chunks c
    WHERE c.embed_model_id = $1        -- CRITICAL: never omit this
      AND 1 - (c.embedding <=> $2::vector) > $3
    ...
"""
rows = await db.fetch(sql, settings.embedding_model, embedding, min_similarity)
```

---

## Alembic Setup

```bash
pip install alembic sqlalchemy[asyncio]
alembic init alembic
```

**alembic/env.py (async):**
```python
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

def run_migrations_online():
    url = os.environ["DATABASE_URL_DIRECT"].replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(url)
    async def do_run():
        async with engine.connect() as conn:
            await conn.run_sync(context.run_migrations)
    asyncio.run(do_run())

run_migrations_online()
```

**Run on app startup (main.py lifespan):**
```python
from alembic.config import Config
from alembic import command

async def lifespan(app):
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url",
        settings.database_url_direct.replace("postgresql://","postgresql+asyncpg://"))
    command.upgrade(cfg, "head")   # runs before pool opens
    await create_pool()
    yield
    await close_pool()
```

---

## Migration File Template

```python
# alembic/versions/002_add_embed_model_id.py
"""Add embed_model_id to chunks
Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'

def upgrade():
    op.add_column('chunks',
        sa.Column('embed_model_id', sa.String(64), nullable=False,
                  server_default='nomic-embed-text'))
    op.add_column('chunks',
        sa.Column('embed_model_version', sa.String(32), server_default='1.0'))
    op.create_index('idx_chunks_model', 'chunks', ['embed_model_id'])

def downgrade():
    op.drop_index('idx_chunks_model')
    op.drop_column('chunks', 'embed_model_version')
    op.drop_column('chunks', 'embed_model_id')
```

---

## Model Upgrade Script

```python
# scripts/rembed_chunks.py
async def rembed_all_chunks(new_model: str, batch_size: int = 100, dry_run: bool = False):
    await create_pool()
    pool = await get_pool()
    service = EmbeddingService(provider=detect_provider(new_model), model=new_model)

    async with pool.acquire() as db:
        total = await db.fetchval(
            "SELECT COUNT(*) FROM chunks WHERE embed_model_id != $1", new_model
        )
        print(f"Chunks to re-embed: {total}")
        if dry_run: return

        offset = 0
        while True:
            rows = await db.fetch("""
                SELECT id, chunk_text FROM chunks
                WHERE embed_model_id != $1
                ORDER BY id LIMIT $2 OFFSET $3
            """, new_model, batch_size, offset)
            if not rows: break
            embeddings = await service.embed_batch([r["chunk_text"] for r in rows])
            async with db.transaction():
                for row, emb in zip(rows, embeddings):
                    await db.execute("""
                        UPDATE chunks SET embedding=$1::vector,
                          embed_model_id=$2, embed_model_version=$3
                        WHERE id=$4
                    """, str(emb), new_model, "1.0", row["id"])
            offset += len(rows)
```

**Safe upgrade order:**
```bash
python scripts/rembed_chunks.py --model text-embedding-3-small --dry-run
python scripts/rembed_chunks.py --model text-embedding-3-small
# verify: SELECT embed_model_id, COUNT(*) FROM chunks GROUP BY 1
# then: update settings.embedding_model and deploy
```

---

## Supabase Connection Pooling

```python
# config.py + .env.example
# App connections → pooler URL (port 6543)
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:6543/postgres?pgbouncer=true
# Migrations only → direct URL (port 5432)
DATABASE_URL_DIRECT=postgresql://user:pass@db.xxx.supabase.co:5432/postgres

# database.py
_pool = await asyncpg.create_pool(
    settings.database_url,
    min_size=settings.db_pool_min_size,   # 1
    max_size=settings.db_pool_max_size,   # 5 — NEVER higher on Supabase free
    server_settings={"jit": "off"},       # required for Supabase compatibility
)
```

---

## File Locations

```
alembic/
  env.py
  versions/
    001_initial_schema.py
    002_add_embed_model_id.py
    003_add_trace_id_agent_runs.py
    004_add_rate_limit.py
    005_retention_indexes.py
alembic.ini
scripts/rembed_chunks.py
```