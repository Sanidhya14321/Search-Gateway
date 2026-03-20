import asyncio
import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database import close_pool, create_pool, get_pool
from backend.services.embedding_service import EmbeddingService
from backend.config import settings


async def rembed_chunks(old_model: str, new_model: str, batch_size: int, limit: int | None) -> int:
    await create_pool()
    pool = await get_pool()
    embed_service = EmbeddingService(model=new_model, dimensions=settings.embedding_dimensions)
    updated = 0

    try:
        async with pool.acquire() as db:
            while True:
                if limit is not None and updated >= limit:
                    break

                remaining = batch_size if limit is None else min(batch_size, max(limit - updated, 0))
                if remaining <= 0:
                    break

                rows = await db.fetch(
                    """
                    SELECT id, chunk_text
                    FROM chunks
                    WHERE embed_model_id = $1
                    ORDER BY id
                    LIMIT $2
                    """,
                    old_model,
                    remaining,
                )
                if not rows:
                    break

                texts = [str(row["chunk_text"]) for row in rows]
                vectors = await embed_service.embed_batch(texts, batch_size=min(100, len(texts)))

                for row, vector in zip(rows, vectors, strict=True):
                    await db.execute(
                        """
                        UPDATE chunks
                        SET embedding = $1::vector,
                            embed_model_id = $2,
                            updated_at = NOW()
                        WHERE id = $3
                        """,
                        vector,
                        new_model,
                        row["id"],
                    )
                updated += len(rows)

                if len(rows) < remaining:
                    break
    finally:
        await close_pool()

    return updated


async def main() -> None:
    parser = argparse.ArgumentParser(description="Re-embed chunks from old model to a new model.")
    parser.add_argument("--old-model", required=True)
    parser.add_argument("--new-model", default=settings.embedding_model)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    total = await rembed_chunks(
        old_model=args.old_model,
        new_model=args.new_model,
        batch_size=max(1, args.batch_size),
        limit=args.limit,
    )
    print(f"Re-embedded chunks: {total}")


if __name__ == "__main__":
    asyncio.run(main())
