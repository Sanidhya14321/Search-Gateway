from backend.agents.state import CRMindState
from backend.services.entity_resolver import resolve_entity


async def resolve_entity_node(state: CRMindState) -> dict:
    parsed = state.get("_parsed_filters", {})
    lookup = parsed.get("company_name") or state.get("query", "")

    resolved = await resolve_entity(lookup)
    if resolved is None:
        return {
            "resolved_entity": None,
            "entity_id": None,
            "resolution_confidence": 0.0,
            "steps_log": state.get("steps_log", []) + ["[resolve_entity] not found"],
        }

    return {
        "resolved_entity": resolved.record,
        "entity_id": resolved.record.get("id"),
        "entity_type": resolved.entity_type,
        "resolution_confidence": resolved.confidence,
        "steps_log": state.get("steps_log", [])
        + [f"[resolve_entity] resolved {resolved.canonical_name} confidence={resolved.confidence:.2f}"],
    }
