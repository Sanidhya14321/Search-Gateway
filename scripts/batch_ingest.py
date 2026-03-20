import asyncio
import argparse

from backend.database import close_pool, create_pool, get_pool
from backend.services.embedding_service import build_embedding_service
from backend.crawler.queue_worker import process_crawl_item_by_id
from backend.scoring.batch_refresh import batch_refresh_stale_scores


async def main(stale_only: bool, max_entities: int) -> None:
    await create_pool()
    pool = await get_pool()
    embed_service = build_embedding_service()

    async with pool.acquire() as db:
        if stale_only:
            entities = await db.fetch(
                """
                SELECT id, domain, 'company' AS entity_type
                FROM companies
                WHERE freshness_score < 0.4
                   OR updated_at < NOW() - INTERVAL '7 days'
                LIMIT $1
                """,
                max_entities,
            )
            for entity in entities:
                if not entity["domain"]:
                    continue
                await db.execute(
                    """
                    INSERT INTO crawl_queue (url, domain, entity_id, entity_type, priority)
                    VALUES ($1, $2, $3::uuid, $4::entity_type, 3)
                    """,
                    f"https://{entity['domain']}",
                    entity["domain"],
                    entity["id"],
                    entity["entity_type"],
                )

        pending = await db.fetch(
            "SELECT id FROM crawl_queue WHERE status='pending' ORDER BY priority, created_at LIMIT 200"
        )
        for row in pending:
            await process_crawl_item_by_id(db, embed_service, str(row["id"]))

        await batch_refresh_stale_scores(db, threshold_days=7)

    await close_pool()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stale-only", action="store_true")
    parser.add_argument("--max-entities", type=int, default=200)
    args = parser.parse_args()
    asyncio.run(main(stale_only=args.stale_only, max_entities=args.max_entities))
