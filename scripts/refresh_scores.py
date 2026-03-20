import asyncio
import argparse

from backend.database import close_pool, create_pool, get_pool
from backend.scoring.batch_refresh import batch_refresh_stale_scores


async def main(threshold_days: int) -> None:
    await create_pool()
    pool = await get_pool()
    async with pool.acquire() as db:
        await batch_refresh_stale_scores(db, threshold_days=threshold_days)
    await close_pool()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold-days", type=int, default=7)
    args = parser.parse_args()
    asyncio.run(main(args.threshold_days))
