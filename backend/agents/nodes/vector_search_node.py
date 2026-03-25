from backend.agents.state import CRMindState
from backend.services.retrieval.vector_search import vector_search


async def vector_search_node(state: CRMindState) -> dict:
    try:
        rows = await vector_search(
            query=state.get("query", ""),
            entity_id=state.get("entity_id"),
            entity_type=state.get("entity_type"),
            top_k=20,
        )
        chunks = [row.__dict__ for row in rows]
    except Exception as exc:
        chunks = []
        return {
            "retrieved_chunks": chunks,
            "degraded": True,
            "steps_log": state.get("steps_log", []) + [f"[vector_search] degraded error={type(exc).__name__}"],
        }

    return {
        "retrieved_chunks": chunks,
        "steps_log": state.get("steps_log", []) + [f"[vector_search] retrieved={len(chunks)}"],
    }
