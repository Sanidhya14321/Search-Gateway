from fastapi import APIRouter, Depends

from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/entity", tags=["entities"])


@router.get("/{canonical_id}")
async def entity_detail(
    canonical_id: str,
    db=Depends(get_db_connection),
    _: AuthenticatedUser = Depends(get_current_user),
):
    company = await db.fetchrow("SELECT * FROM companies WHERE canonical_id=$1", canonical_id)
    person = None if company else await db.fetchrow("SELECT * FROM people WHERE canonical_id=$1", canonical_id)

    # Accept UUID paths from older frontend links as a fallback.
    if company is None and person is None:
        company = await db.fetchrow("SELECT * FROM companies WHERE id::text=$1", canonical_id)
        if company is None:
            person = await db.fetchrow("SELECT * FROM people WHERE id::text=$1", canonical_id)

    if company:
        entity_id = company["id"]
        entity_type = "company"
        canonical_name = company["canonical_name"]
    elif person:
        entity_id = person["id"]
        entity_type = "person"
        canonical_name = person["full_name"]
    else:
        return {"entity_id": canonical_id, "entity_type": "unknown", "degraded": True, "facts": [], "signals": [], "people": [], "citations": []}

    facts = [dict(row) for row in await db.fetch("SELECT claim, confidence, source_url FROM facts WHERE entity_id=$1::uuid ORDER BY extracted_at DESC LIMIT 25", entity_id)]
    signals = [dict(row) for row in await db.fetch("SELECT signal_type, description, confidence, source_url, detected_at FROM signals WHERE entity_id=$1::uuid ORDER BY detected_at DESC LIMIT 25", entity_id)]

    people = []
    roles = []
    if entity_type == "company":
        people = [
            dict(row)
            for row in await db.fetch(
                "SELECT full_name, current_title, seniority_level, linkedin_url FROM people WHERE current_company_id=$1::uuid LIMIT 50",
                entity_id,
            )
        ]
    else:
        roles = [
            dict(row)
            for row in await db.fetch(
                "SELECT title, is_current, start_date, end_date, source_url FROM roles WHERE person_id=$1::uuid ORDER BY start_date DESC",
                entity_id,
            )
        ]

    citations = [
        dict(row)
        for row in await db.fetch(
            "SELECT source_url AS url, source_type, fetched_at, trust_score, freshness_score FROM source_documents WHERE entity_id=$1::uuid ORDER BY fetched_at DESC LIMIT 25",
            entity_id,
        )
    ]

    return {
        "entity_id": canonical_id,
        "entity_type": entity_type,
        "canonical_name": canonical_name,
        "confidence": 0.9,
        "summary": None,
        "degraded": False,
        "facts": facts,
        "signals": signals,
        "people": people,
        "roles": roles,
        "citations": citations,
    }
