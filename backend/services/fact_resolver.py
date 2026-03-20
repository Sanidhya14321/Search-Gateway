def _normalize_claim(claim: str) -> str:
    return " ".join(claim.strip().lower().split())


async def resolve_fact_conflicts(facts: list[dict]) -> list[dict]:
    """Merge duplicate facts by claim and keep the highest-confidence version.

    If multiple facts share the same normalized claim, retain the one with the
    highest confidence and merge unique citations from all duplicates.
    """
    merged: dict[str, dict] = {}

    for fact in facts:
        claim = str(fact.get("claim") or "").strip()
        if not claim:
            continue

        key = _normalize_claim(claim)
        candidate = {
            "claim": claim,
            "confidence": float(fact.get("confidence", 0.0)),
            "citations": list(fact.get("citations") or []),
        }

        existing = merged.get(key)
        if existing is None or candidate["confidence"] > existing["confidence"]:
            merged[key] = candidate
        else:
            existing_citations = existing.get("citations", [])
            seen_urls = {str(item.get("url", "")) for item in existing_citations if isinstance(item, dict)}
            for citation in candidate["citations"]:
                if not isinstance(citation, dict):
                    continue
                url = str(citation.get("url", ""))
                if url and url not in seen_urls:
                    existing_citations.append(citation)
                    seen_urls.add(url)
            existing["citations"] = existing_citations

    resolved = list(merged.values())
    resolved.sort(key=lambda item: float(item.get("confidence", 0.0)), reverse=True)
    return resolved
