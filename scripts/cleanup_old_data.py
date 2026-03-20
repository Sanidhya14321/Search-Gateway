import asyncio

from backend.database import close_pool, create_pool, get_pool


async def main() -> None:
    await create_pool()
    pool = await get_pool()

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

    await close_pool()
    print(f"cleanup_old_data | cache_deleted={cache_deleted} agent_runs_deleted={agent_deleted}")
    return None


if __name__ == "__main__":
    asyncio.run(main())
