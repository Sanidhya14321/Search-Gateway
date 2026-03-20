from backend.scoring.freshness import compute_freshness_for_source
from backend.scoring.trust import compute_trust_score


async def refresh_entity_scores(entity_id: str, entity_type: str, db) -> None:
    rows = await db.fetch(
        """
        SELECT source_type, fetched_at
        FROM source_documents
        WHERE entity_id = $1::uuid AND entity_type = $2::entity_type
        ORDER BY fetched_at DESC
        LIMIT 20
        """,
        entity_id,
        entity_type,
    )

    if not rows:
        return

    freshness_scores = [compute_freshness_for_source(row["fetched_at"], row["source_type"]) for row in rows]
    trust_scores = [compute_trust_score(row["source_type"]) for row in rows]

    avg_freshness = sum(freshness_scores) / len(freshness_scores)
    weighted_freshness = (freshness_scores[0] * 0.5) + (avg_freshness * 0.5)
    avg_trust = sum(trust_scores) / len(trust_scores)

    if entity_type == "company":
        await db.execute(
            "UPDATE companies SET freshness_score=$1, trust_score=$2, updated_at=NOW() WHERE id=$3::uuid",
            weighted_freshness,
            avg_trust,
            entity_id,
        )
    elif entity_type == "person":
        await db.execute(
            "UPDATE people SET freshness_score=$1, trust_score=$2, updated_at=NOW() WHERE id=$3::uuid",
            weighted_freshness,
            avg_trust,
            entity_id,
        )


async def batch_refresh_stale_scores(db, threshold_days: int = 7) -> None:
    stale = await db.fetch(
        """
        SELECT id, 'company' AS entity_type
        FROM companies
        WHERE updated_at < NOW() - ($1 * INTERVAL '1 day')
        UNION ALL
        SELECT id, 'person' AS entity_type
        FROM people
        WHERE updated_at < NOW() - ($1 * INTERVAL '1 day')
        """,
        threshold_days,
    )

    for entity in stale:
        await refresh_entity_scores(str(entity["id"]), str(entity["entity_type"]), db)
