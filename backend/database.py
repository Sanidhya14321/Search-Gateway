import asyncpg
import pgvector.asyncpg
from inspect import isawaitable

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


async def resolve_pool(pool_candidate: object | None = None) -> asyncpg.Pool:
    """Resolve a pool from async/sync candidates, with lazy fallback.

    This keeps runtime code and tests compatible when get_pool is monkeypatched
    to a synchronous lambda returning a pool.
    """
    candidate = get_pool() if pool_candidate is None else pool_candidate
    pool = await candidate if isawaitable(candidate) else candidate
    if pool is None:
        pool = await create_pool()
    return pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        try:
            await _pool.close()
        except RuntimeError as exc:
            # Can happen in test teardown when an orphan task kept a pool bound
            # to a loop that is already closed.
            if "Event loop is closed" in str(exc):
                _pool.terminate()
            else:
                raise
        _pool = None
