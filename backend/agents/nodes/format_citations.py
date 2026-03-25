from backend.agents.state import CRMindState
from backend.services.citations.formatter import format_citations_for_response


async def format_citations_node(state: CRMindState) -> dict:
    final_response = state.get("final_response") or {}
    ranked_chunks = state.get("ranked_chunks", [])
    try:
        enhanced = await format_citations_for_response(final_response, ranked_chunks)
    except Exception as exc:
        fallback = dict(final_response) if isinstance(final_response, dict) else {}
        fallback.setdefault("citations", [])
        fallback["degraded"] = True
        return {
            "final_response": fallback,
            "citations": fallback.get("citations", []),
            "degraded": True,
            "steps_log": state.get("steps_log", []) + [f"[format_citations] degraded error={type(exc).__name__}"],
        }

    return {
        "final_response": enhanced,
        "citations": enhanced.get("citations", []),
        "steps_log": state.get("steps_log", []) + ["[format_citations] attached citations"],
    }
