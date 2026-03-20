from backend.agents.state import CRMindState
from backend.services.citations.formatter import format_citations_for_response


async def format_citations_node(state: CRMindState) -> dict:
    final_response = state.get("final_response") or {}
    ranked_chunks = state.get("ranked_chunks", [])
    enhanced = await format_citations_for_response(final_response, ranked_chunks)
    return {
        "final_response": enhanced,
        "citations": enhanced.get("citations", []),
        "steps_log": state.get("steps_log", []) + ["[format_citations] attached citations"],
    }
