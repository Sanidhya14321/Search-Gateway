import asyncpg
from loguru import logger

try:
    from arq import cron
    from arq.connections import RedisSettings
except Exception:  # pragma: no cover - arq optional for local test runtime
    def cron(function, **kwargs):
        _ = kwargs
        return function

    class RedisSettings:
        @classmethod
        def from_dsn(cls, dsn: str):
            _ = dsn
            return cls()

from backend.config import settings
from backend.crawler.queue_worker import process_crawl_item_by_id
from backend.services.embedding_service import embedding_service
from backend.scoring.batch_refresh import batch_refresh_stale_scores


async def startup(ctx: dict) -> None:
    ctx["pool"] = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=5,
    )
    ctx["embed_service"] = embedding_service


async def shutdown(ctx: dict) -> None:
    pool = ctx.get("pool")
    if pool is not None:
        await pool.close()


async def crawl_task(ctx: dict, crawl_item_id: str) -> None:
    pool = ctx.get("pool")
    if pool is None:
        return None

    embed_service = ctx.get("embed_service")
    async with pool.acquire() as db:
        await process_crawl_item_by_id(db, embed_service, crawl_item_id)
    return None


async def refresh_scores_task(ctx: dict) -> None:
    pool = ctx.get("pool")
    if pool is None:
        return None
    async with pool.acquire() as db:
        await batch_refresh_stale_scores(db, threshold_days=7)
    return None


async def cleanup_task(ctx: dict) -> None:
    pool = ctx.get("pool")
    if pool is None:
        return None

    async with pool.acquire() as db:
        cache_result = await db.execute(
            "DELETE FROM query_cache WHERE expires_at < NOW() - (7 * INTERVAL '1 day')"
        )
        cache_deleted = int(cache_result.split()[-1])

        agent_result = await db.execute(
            """
            DELETE FROM agent_runs
            WHERE created_at < NOW() - (90 * INTERVAL '1 day')
              AND status = 'completed'
            """
        )
        agent_deleted = int(agent_result.split()[-1])

    logger.info("cleanup_task | cache_deleted={} agent_runs_deleted={}", cache_deleted, agent_deleted)
    return None


class WorkerSettings:
    functions = [crawl_task]
    cron_jobs = [
        cron(refresh_scores_task, hour=2, minute=0),
        cron(cleanup_task, weekday=0, hour=3, minute=0),
    ]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 5
