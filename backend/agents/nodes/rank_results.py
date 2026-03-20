from backend.agents.state import CRMindState
from backend.services.retrieval.keyword_search import keyword_search
from backend.services.retrieval.merger import merge_results_rrf
from backend.services.retrieval.ranker import rank_chunks
from backend.services.retrieval.vector_search import ChunkResult


async def rank_results_node(state: CRMindState) -> dict:
    vector_chunks = [ChunkResult(**chunk) for chunk in state.get("retrieved_chunks", [])]
    keyword_chunks = await keyword_search(
        query=state.get("query", ""),
        entity_id=state.get("entity_id"),
        top_k=20,
    )

    merged = merge_results_rrf(vector_chunks, keyword_chunks)
    ranked = rank_chunks(merged)
    ranked_dicts = [chunk.__dict__ for chunk in ranked]
    return {
        "ranked_chunks": ranked_dicts,
        "steps_log": state.get("steps_log", []) + [f"[rank_results] ranked={len(ranked_dicts)}"],
    }
