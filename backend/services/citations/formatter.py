from backend.services.citations.builder import build_citation
from backend.services.citations.finder import find_supporting_chunks


async def format_citations_for_response(response: dict, ranked_chunks: list[dict]) -> dict:
    facts_out = []
    people_out = []

    for idx, fact in enumerate(response.get("facts", [])):
        claim = str(fact.get("claim", ""))
        matched = await find_supporting_chunks(claim, ranked_chunks, top_k=3)
        facts_out.append(
            {
                "fact_id": f"fact_{idx:03d}",
                "claim": claim,
                "confidence": float(fact.get("confidence", 0.5)),
                "citations": [build_citation(chunk) for chunk in matched],
            }
        )

    for person in response.get("people", []):
        person_query = f"{person.get('name', '')} {person.get('title', '')}".strip()
        matched = await find_supporting_chunks(person_query, ranked_chunks, top_k=2)
        people_out.append(
            {
                "canonical_id": str(person.get("canonical_id", "")),
                "full_name": str(person.get("name", person.get("full_name", ""))),
                "current_title": person.get("title", person.get("current_title")),
                "seniority_level": str(person.get("seniority", person.get("seniority_level", "unknown"))),
                "confidence": float(person.get("confidence", 0.5)),
                "citations": [build_citation(chunk) for chunk in matched],
            }
        )

    citation_map: dict[str, dict] = {}
    for entry in facts_out:
        for citation in entry["citations"]:
            if citation["url"] and citation["url"] not in citation_map:
                citation_map[citation["url"]] = citation
    for entry in people_out:
        for citation in entry["citations"]:
            if citation["url"] and citation["url"] not in citation_map:
                citation_map[citation["url"]] = citation

    return {
        **response,
        "facts": facts_out,
        "people": people_out,
        "citations": list(citation_map.values()),
        "citation_count": len(citation_map),
    }
