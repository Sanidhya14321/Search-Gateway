from datetime import datetime, timezone


def assemble_final_response(
    entity: dict,
    synthesis: dict,
    cited_facts: list[dict],
    cited_people: list[dict],
    signals: list[dict],
    confidence: float,
) -> dict:
    all_citations: list[dict] = []
    for fact in cited_facts:
        all_citations.extend(fact.get("citations", []))
    for person in cited_people:
        all_citations.extend(person.get("citations", []))

    citation_map: dict[str, dict] = {}
    for citation in all_citations:
        url = citation.get("url")
        if url and url not in citation_map:
            citation_map[url] = citation

    return {
        "entity_id": entity.get("canonical_id") or entity.get("id"),
        "entity_type": entity.get("entity_type", "company"),
        "canonical_name": entity.get("canonical_name"),
        "confidence": confidence,
        "summary": synthesis.get("summary", ""),
        "degraded": bool(synthesis.get("degraded", False)),
        "facts": cited_facts,
        "signals": signals,
        "people": cited_people,
        "citations": list(citation_map.values()),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "1.0.0",
    }
