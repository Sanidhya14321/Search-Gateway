from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_optional_user
from backend.services.user_service import record_search
from backend.services.entity_resolver import resolve_entity
from backend.services.retrieval.ranker import rank_chunks
from backend.services.retrieval.vector_search import vector_search
from loguru import logger

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    entity_type: str | None = None
    filters: dict | None = None


@router.post("")
async def search_endpoint(
    payload: SearchRequest,
    db=Depends(get_db_connection),
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
):
    query = payload.query.strip()
    resolved = await resolve_entity(query)

    rows = await db.fetch(
        """
        SELECT canonical_id, canonical_name, domain,
               similarity(canonical_name, $1) AS sim
        FROM companies
        WHERE similarity(canonical_name, $1) > 0.3
        ORDER BY sim DESC
        LIMIT 5
        """,
        query,
    )
    candidates = [
        {
            "canonical_id": row["canonical_id"],
            "canonical_name": row["canonical_name"],
            "confidence": float(row["sim"]),
            "match_type": "fuzzy",
            "domain": row["domain"],
        }
        for row in rows
    ]
    if resolved is not None:
        candidates.insert(
            0,
            {
                "canonical_id": resolved.canonical_id,
                "canonical_name": resolved.canonical_name,
                "confidence": resolved.confidence,
                "match_type": resolved.match_type,
                "domain": resolved.record.get("domain"),
            },
        )

    chunks = []
    try:
        chunks = await vector_search(query, entity_id=str(resolved.record.get("id")) if resolved else None, top_k=8)
    except Exception as exc:
        logger.warning("search_vector_degraded | error={}", type(exc).__name__)
    ranked = rank_chunks(chunks)
    context_preview = [
        {
            "chunk_text": chunk.chunk_text,
            "source_url": chunk.source_url,
            "similarity": chunk.similarity,
            "final_score": chunk.final_score,
        }
        for chunk in ranked[:3]
    ]

    response = {
        "query": query,
        "candidates": candidates[:5],
        "context_preview": context_preview,
    }

    if current_user is not None:
        await record_search(
            db=db,
            user_id=current_user.user_id,
            query=query,
            workflow_name="search",
            agent_run_id=None,
            entity_id=str(resolved.record.get("id")) if resolved else None,
            entity_name=resolved.canonical_name if resolved else None,
            entity_type=resolved.entity_type if resolved else payload.entity_type,
            result_count=len(context_preview),
        )

    return response


@router.get("")
async def search_endpoint_get(
    q: str = Query(..., min_length=1),
    db=Depends(get_db_connection),
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
):
    return await search_endpoint(SearchRequest(query=q), db, current_user)
