import hashlib
from collections.abc import Sequence

from backend.config import settings


def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def store_source_document(db, fetched: dict, clean_text: str, content_hash: str, entity_info: dict) -> str:
    domain = entity_info.get("domain")
    if not domain and fetched.get("final_url"):
        domain = fetched["final_url"].split("/")[2] if "/" in fetched["final_url"] else None

    return await db.fetchval(
        """
        INSERT INTO source_documents (
            source_url,
            source_type,
            domain,
            raw_html,
            clean_text,
            entity_id,
            entity_type,
            content_hash,
            http_status,
            crawl_status
        )
        VALUES ($1, $2, $3, $4, $5, $6::uuid, $7::entity_type, $8, $9, 'completed')
        RETURNING id
        """,
        fetched["url"],
        entity_info.get("source_type", "unknown"),
        domain,
        fetched.get("raw_html", ""),
        clean_text,
        entity_info.get("entity_id"),
        entity_info.get("entity_type"),
        content_hash,
        fetched.get("status", 0),
    )


async def embed_and_store_chunks(
    db,
    embed_service,
    doc_id: str,
    chunks: Sequence[dict],
    entity_info: dict,
) -> None:
    if not chunks:
        return

    chunk_texts = [str(chunk["chunk_text"]) for chunk in chunks]
    embeddings = await embed_service.embed_batch(chunk_texts, batch_size=100)

    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append(
            (
                doc_id,
                int(chunk["chunk_index"]),
                chunk["chunk_text"],
                int(chunk["char_start"]),
                int(chunk["char_end"]),
                int(chunk["token_count"]),
                entity_info.get("entity_id"),
                entity_info.get("entity_type"),
                float(entity_info.get("freshness_score", 0.5)),
                float(entity_info.get("trust_score", 0.5)),
                embedding,
                settings.embedding_model,
            )
        )

    await db.executemany(
        """
        INSERT INTO chunks (
            source_doc_id,
            chunk_index,
            chunk_text,
            char_start,
            char_end,
            token_count,
            entity_id,
            entity_type,
            freshness_score,
            trust_score,
            embedding,
            embed_model_id
        )
        VALUES ($1::uuid, $2, $3, $4, $5, $6, $7::uuid, $8::entity_type, $9, $10, $11::vector, $12)
        """,
        rows,
    )
