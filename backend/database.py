import asyncpg
import pgvector.asyncpg

from backend.config import settings

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    # Ensure vector type exists before registering codec in local/dev databases.
    await conn.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    await pgvector.asyncpg.register_vector(conn)


async def create_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            command_timeout=30,
            server_settings={"jit": "off"},
            init=_init_connection,
        )
    return _pool


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        return await create_pool()
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
