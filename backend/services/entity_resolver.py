from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import asyncpg

from backend.config import settings
from backend.database import get_pool
from backend.services.embedding_service import EmbeddingService


@dataclass
class ResolvedEntity:
    canonical_id: str
    entity_type: str
    canonical_name: str
    confidence: float
    match_type: str
    record: dict[str, Any]
    alternatives: list[dict[str, Any]]


def normalize_domain(value: str) -> str:
    text = value.strip().lower()
    if not text:
        return ""

    candidate = text
    if "://" in candidate:
        candidate = urlparse(candidate).netloc or candidate
    if "/" in candidate:
        candidate = candidate.split("/", 1)[0]
    if "@" in candidate:
        candidate = candidate.rsplit("@", 1)[-1]
    if candidate.startswith("www."):
        candidate = candidate[4:]
    return candidate.rstrip(".")


def _normalize_name(value: str) -> str:
    name = value.strip().lower()
    for suffix in (" inc", " llc", " ltd", " corp", " corporation", " co"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return " ".join(name.split())


def _score_match(match_type: str) -> float:
    base = {
        "exact_domain": 0.98,
        "exact_name": 0.95,
        "fuzzy": 0.70,
        "alias": 0.88,
        "embedding": 0.55,
    }
    return base.get(match_type, 0.0)


def _resolved_from_row(
    row: asyncpg.Record,
    *,
    match_type: str,
    confidence: float,
    alternatives: list[dict[str, Any]],
) -> ResolvedEntity:
    payload = dict(row)
    return ResolvedEntity(
        canonical_id=str(payload["canonical_id"]),
        entity_type="company",
        canonical_name=str(payload["canonical_name"]),
        confidence=confidence,
        match_type=match_type,
        record=payload,
        alternatives=alternatives,
    )


async def resolve_entity(raw_query: str) -> ResolvedEntity | None:
    query = raw_query.strip()
    if not query:
        return None

    pool = await get_pool()
    normalized_domain = normalize_domain(query)
    normalized_name = _normalize_name(query)

    async with pool.acquire() as db:
        # Step 1: exact domain match
        if normalized_domain:
            domain_row = await db.fetchrow(
                """
                SELECT *
                FROM companies
                WHERE domain = $1
                LIMIT 1
                """,
                normalized_domain,
            )
            if domain_row is not None:
                confidence = _score_match("exact_domain")
                return _resolved_from_row(
                    domain_row,
                    match_type="exact_domain",
                    confidence=confidence,
                    alternatives=[],
                )

        # Step 2: fuzzy pg_trgm match
        fuzzy_rows = await db.fetch(
            """
            SELECT *, similarity(canonical_name, $1) AS sim
            FROM companies
            WHERE similarity(canonical_name, $1) > 0.4
            ORDER BY sim DESC
            LIMIT 5
            """,
            normalized_name,
        )
        if fuzzy_rows:
            best = fuzzy_rows[0]
            best_name = _normalize_name(str(best["canonical_name"]))
            match_type = "exact_name" if best_name == normalized_name else "fuzzy"
            confidence = min(1.0, _score_match(match_type) + (float(best["sim"]) * 0.2))
            alternatives = [
                {
                    "canonical_id": row["canonical_id"],
                    "canonical_name": row["canonical_name"],
                    "confidence": min(1.0, _score_match("fuzzy") + (float(row["sim"]) * 0.2)),
                    "match_type": "fuzzy",
                }
                for row in fuzzy_rows[1:]
            ]
            if confidence >= 0.6:
                return _resolved_from_row(
                    best,
                    match_type=match_type,
                    confidence=confidence,
                    alternatives=alternatives,
                )

        # Step 3: alias array match
        alias_row = await db.fetchrow(
            """
            SELECT *
            FROM companies
            WHERE $1 = ANY(aliases)
            LIMIT 1
            """,
            normalized_name,
        )
        if alias_row is not None:
            confidence = _score_match("alias")
            if confidence >= 0.6:
                return _resolved_from_row(
                    alias_row,
                    match_type="alias",
                    confidence=confidence,
                    alternatives=[],
                )

        # Step 4: embedding fallback (only if steps 1-3 return nothing)
        try:
            embed_service = EmbeddingService(
                model=settings.embedding_model,
                dimensions=settings.embedding_dimensions,
            )
            query_vector = await embed_service.embed(query)
            embedding_rows = await db.fetch(
                """
                SELECT c.*, (e.embedding <=> $1::vector) AS dist
                FROM company_embeddings e
                JOIN companies c ON c.id = e.company_id
                ORDER BY dist ASC
                LIMIT 3
                """,
                query_vector,
            )
        except Exception:
            embedding_rows = []

        if embedding_rows:
            best = embedding_rows[0]
            dist = float(best["dist"])
            confidence = max(0.0, min(1.0, _score_match("embedding") + (1.0 - dist) * 0.25))
            if confidence >= 0.6:
                alternatives = [
                    {
                        "canonical_id": row["canonical_id"],
                        "canonical_name": row["canonical_name"],
                        "confidence": max(0.0, min(1.0, _score_match("embedding") + (1.0 - float(row["dist"])) * 0.25)),
                        "match_type": "embedding",
                    }
                    for row in embedding_rows[1:]
                ]
                return _resolved_from_row(
                    best,
                    match_type="embedding",
                    confidence=confidence,
                    alternatives=alternatives,
                )

    # Step 5 threshold gate: never create a new entity silently.
    return None
