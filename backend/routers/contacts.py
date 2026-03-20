from fastapi import APIRouter, Depends

from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/contact", tags=["contacts"])


@router.get("/{canonical_id}")
async def contact_detail(
    canonical_id: str,
    db=Depends(get_db_connection),
    _: AuthenticatedUser = Depends(get_current_user),
):
    person = await db.fetchrow("SELECT * FROM people WHERE canonical_id=$1", canonical_id)
    if person is None:
        return {"canonical_id": canonical_id, "degraded": True, "roles": [], "citations": []}

    roles = [
        dict(row)
        for row in await db.fetch(
            "SELECT title, seniority_level, department, start_date, end_date, is_current, source_url FROM roles WHERE person_id=$1::uuid ORDER BY start_date DESC",
            person["id"],
        )
    ]
    citations = [
        dict(row)
        for row in await db.fetch(
            """
            SELECT source_url AS url, source_type, fetched_at, trust_score, freshness_score
            FROM source_documents
            WHERE entity_id=$1::uuid OR source_url = ANY(
                SELECT source_url FROM roles WHERE person_id=$1::uuid AND source_url IS NOT NULL
            )
            ORDER BY fetched_at DESC
            LIMIT 20
            """,
            person["id"],
        )
    ]

    return {
        "canonical_id": canonical_id,
        "full_name": person["full_name"],
        "current_title": person["current_title"],
        "seniority_level": person["seniority_level"],
        "roles": roles,
        "citations": citations,
    }
