from backend.database import get_pool
from backend.services.retrieval.vector_search import ChunkResult


async def keyword_search(query: str, entity_id: str | None = None, top_k: int = 20, db=None) -> list[ChunkResult]:
    if db is not None:
        rows = await db.fetch(
            """
            SELECT
                c.id,
                c.chunk_text,
                c.source_doc_id,
                c.entity_id,
                c.freshness_score,
                c.trust_score,
                sd.source_url,
                sd.source_type,
                sd.fetched_at,
                ts_rank(to_tsvector('english', c.chunk_text), plainto_tsquery('english', $1)) AS similarity
            FROM chunks c
            JOIN source_documents sd ON sd.id = c.source_doc_id
            WHERE to_tsvector('english', c.chunk_text) @@ plainto_tsquery('english', $1)
              AND ($2::uuid IS NULL OR c.entity_id = $2::uuid)
            ORDER BY similarity DESC
            LIMIT $3
            """,
            query,
            entity_id,
            top_k,
        )
    else:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    c.id,
                    c.chunk_text,
                    c.source_doc_id,
                    c.entity_id,
                    c.freshness_score,
                    c.trust_score,
                    sd.source_url,
                    sd.source_type,
                    sd.fetched_at,
                    ts_rank(to_tsvector('english', c.chunk_text), plainto_tsquery('english', $1)) AS similarity
                FROM chunks c
                JOIN source_documents sd ON sd.id = c.source_doc_id
                WHERE to_tsvector('english', c.chunk_text) @@ plainto_tsquery('english', $1)
                  AND ($2::uuid IS NULL OR c.entity_id = $2::uuid)
                ORDER BY similarity DESC
                LIMIT $3
                """,
                query,
                entity_id,
                top_k,
            )

    if rows:
        max_rank = max(float(row.get("similarity", 0.0)) for row in rows) or 1.0
        return [
            ChunkResult(
                id=str(row["id"]),
                chunk_text=str(row["chunk_text"]),
                source_doc_id=str(row["source_doc_id"]),
                entity_id=str(row["entity_id"]) if row["entity_id"] is not None else None,
                similarity=float(row.get("similarity", 0.0)) / max_rank,
                freshness_score=float(row.get("freshness_score", 0.5)),
                trust_score=float(row.get("trust_score", 0.5)),
                source_url=str(row.get("source_url", "")),
                source_type=str(row.get("source_type", "unknown")),
                fetched_at=row.get("fetched_at"),
                final_score=float(row.get("final_score", 0.0)),
                retrieval_source="keyword",
            )
            for row in rows
        ]

    return []
