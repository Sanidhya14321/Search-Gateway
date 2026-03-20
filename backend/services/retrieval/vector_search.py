from dataclasses import dataclass
from datetime import datetime

from backend.config import settings
from backend.database import get_pool
from backend.services.embedding_service import build_embedding_service


@dataclass
class ChunkResult:
    id: str
    chunk_text: str
    source_doc_id: str
    entity_id: str | None
    source_url: str
    source_type: str
    fetched_at: datetime | None
    similarity: float
    freshness_score: float = 0.5
    trust_score: float = 0.5
    final_score: float = 0.0
    retrieval_source: str = "vector"


async def vector_search(
    query: str,
    entity_id: str | None = None,
    entity_type: str | None = None,
    top_k: int = 20,
    min_similarity: float | None = None,
    db=None,
    embed_service=None,
) -> list[ChunkResult]:
    similarity_threshold = min_similarity if min_similarity is not None else settings.min_similarity
    embedder = embed_service or build_embedding_service()
    query_embedding = await embedder.embed(query)

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
                1 - (c.embedding <=> $1::vector) AS similarity
            FROM chunks c
            JOIN source_documents sd ON sd.id = c.source_doc_id
            WHERE 1 - (c.embedding <=> $1::vector) > $2
              AND c.embed_model_id = $3
              AND ($4::uuid IS NULL OR c.entity_id = $4::uuid)
              AND ($5::entity_type IS NULL OR c.entity_type = $5::entity_type)
            ORDER BY c.embedding <=> $1::vector
            LIMIT $6
            """,
            query_embedding,
            similarity_threshold,
            settings.embedding_model,
            entity_id,
            entity_type,
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
                    1 - (c.embedding <=> $1::vector) AS similarity
                FROM chunks c
                JOIN source_documents sd ON sd.id = c.source_doc_id
                WHERE 1 - (c.embedding <=> $1::vector) > $2
                  AND c.embed_model_id = $3
                  AND ($4::uuid IS NULL OR c.entity_id = $4::uuid)
                  AND ($5::entity_type IS NULL OR c.entity_type = $5::entity_type)
                ORDER BY c.embedding <=> $1::vector
                LIMIT $6
                """,
                query_embedding,
                similarity_threshold,
                settings.embedding_model,
                entity_id,
                entity_type,
                top_k,
            )

    return [
        ChunkResult(
            id=str(row["id"]),
            chunk_text=str(row["chunk_text"]),
            source_doc_id=str(row["source_doc_id"]),
            entity_id=str(row["entity_id"]) if row["entity_id"] is not None else None,
            freshness_score=float(row["freshness_score"]),
            trust_score=float(row["trust_score"]),
            source_url=str(row["source_url"]),
            source_type=str(row["source_type"]),
            fetched_at=row["fetched_at"],
            similarity=float(row["similarity"]),
            retrieval_source="vector",
        )
        for row in rows
    ]
