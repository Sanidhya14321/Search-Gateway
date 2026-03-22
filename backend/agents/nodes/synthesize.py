from backend.agents import llm_client
from backend.agents.state import CRMindState
from backend.services.retrieval.context_assembler import assemble_context

async def llm_json_call(prompt: str, system: str = "", model=None):
    # Keep an indirection so tests can patch either this symbol or llm_client.
    return await llm_client.llm_json_call_with_fallback(prompt, system=system, model=model)


async def synthesize_node(state: CRMindState) -> dict:
    context = assemble_context([])
    ranked = state.get("ranked_chunks", [])
    if ranked:
        try:
            from backend.services.retrieval.vector_search import ChunkResult

            context = assemble_context([ChunkResult(**chunk) for chunk in ranked])
        except Exception:
            context = "\n---\n".join(chunk.get("chunk_text", "") for chunk in ranked)

    system_prompt = (
        "You are a CRM intelligence assistant. "
        "Answer ONLY using provided source context. "
        "If context is missing, return degraded=true and explain that evidence is insufficient."
    )
    prompt = (
        f"Query: {state.get('query', '')}\n"
        f"Context:\n{context}\n"
        "Return JSON with keys: summary, facts, people, signals, degraded."
    )
    synthesis = await llm_json_call(prompt, system=system_prompt)

    return {
        "steps_log": state.get("steps_log", []) + ["[synthesize] synthesized grounded response"],
        "final_response": synthesis,
    }
