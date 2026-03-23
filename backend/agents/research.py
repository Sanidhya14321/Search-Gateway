import asyncio

from backend.agents.graph_runtime import END, START, StateGraph

from backend.agents.llm_client import llm_json_call_with_fallback
from backend.agents.nodes.format_citations import format_citations_node
from backend.agents.state import CRMindState
from backend.services.retrieval.merger import merge_results_rrf
from backend.services.retrieval.ranker import rank_chunks
from backend.services.retrieval.vector_search import vector_search


async def decompose_query_node(state: CRMindState) -> dict:
    prompt = (
        "Break this research question into 3 to 5 sub-questions and return JSON with key sub_questions.\n"
        f"Query: {state.get('query', '')}"
    )
    try:
        data = await llm_json_call_with_fallback(prompt)
        sub_questions = data.get("sub_questions", []) or [state.get("query", "")]
    except Exception:
        sub_questions = [state.get("query", "")]
    return {"_sub_questions": sub_questions[:5], "steps_log": state.get("steps_log", []) + ["[decompose_query] complete"]}


async def parallel_retrieval_node(state: CRMindState) -> dict:
    sub_questions = state.get("_sub_questions", [])
    tasks = [vector_search(question, entity_id=state.get("entity_id"), entity_type=state.get("entity_type"), top_k=8) for question in sub_questions]
    results = await asyncio.gather(*tasks)

    flattened = []
    for chunk_list in results:
        flattened.extend([chunk.__dict__ for chunk in chunk_list])
    return {"retrieved_chunks": flattened, "steps_log": state.get("steps_log", []) + [f"[parallel_retrieval] chunks={len(flattened)}"]}


async def merge_all_evidence_node(state: CRMindState) -> dict:
    chunk_objs = []
    from backend.services.retrieval.vector_search import ChunkResult

    for chunk in state.get("retrieved_chunks", []):
        chunk_objs.append(ChunkResult(**chunk))
    merged = merge_results_rrf(chunk_objs, [], k=60)
    ranked = rank_chunks(merged)
    return {
        "ranked_chunks": [chunk.__dict__ for chunk in ranked],
        "steps_log": state.get("steps_log", []) + [f"[merge_all_evidence] ranked={len(ranked)}"],
    }


async def synthesize_report_node(state: CRMindState) -> dict:
    ranked = state.get("ranked_chunks", [])
    if not ranked:
        return {
            "final_response": {
                "title": "Research Report",
                "sections": [],
                "facts": [],
                "people": [],
                "signals": [],
                "summary": "Insufficient indexed evidence to answer this query.",
                "degraded": True,
                "confidence": 0.0,
            },
            "steps_log": state.get("steps_log", []) + ["[synthesize_report] no evidence; degraded fallback"],
        }

    context_lines = []
    for idx, chunk in enumerate(ranked[:8], start=1):
        source_url = chunk.get("source_url") or ""
        chunk_text = (chunk.get("chunk_text") or "").strip()
        if chunk_text:
            context_lines.append(f"[{idx}] {chunk_text} | source={source_url}")

    prompt = (
        f"Query: {state.get('query', '')}\n"
        f"Sub-questions: {state.get('_sub_questions', [])}\n"
        f"Evidence:\n{'\\n'.join(context_lines)}\n"
        "Create JSON with keys title and sections where each section has heading, content, citations."
        "Use ONLY the provided evidence. If evidence is insufficient, keep sections empty and set degraded=true."
    )
    report = await llm_json_call_with_fallback(prompt)
    if not isinstance(report, dict):
        report = {}
    report.setdefault("title", "Research Report")
    report.setdefault("sections", [])
    report.setdefault("degraded", False)
    return {"final_response": report, "steps_log": state.get("steps_log", []) + ["[synthesize_report] complete"]}


async def assemble_report_card_node(state: CRMindState) -> dict:
    final = state.get("final_response", {})
    ranked = state.get("ranked_chunks", [])
    assembled = {
        "title": final.get("title", "Research Report"),
        "sections": final.get("sections", []),
        "confidence": 0.8 if ranked else 0.0,
        "degraded": bool(final.get("degraded", not bool(ranked))),
        "summary": final.get("summary", "Insufficient indexed evidence to answer this query." if not ranked else ""),
        "facts": final.get("facts", []),
        "people": final.get("people", []),
        "signals": final.get("signals", []),
    }
    return {"final_response": assembled, "steps_log": state.get("steps_log", []) + ["[assemble_report_card] done"]}


def build_research_graph():
    graph = StateGraph(CRMindState)
    graph.add_node("decompose_query", decompose_query_node)
    graph.add_node("parallel_retrieval", parallel_retrieval_node)
    graph.add_node("merge_all_evidence", merge_all_evidence_node)
    graph.add_node("synthesize_report", synthesize_report_node)
    graph.add_node("assemble_report_card", assemble_report_card_node)
    graph.add_node("format_citations", format_citations_node)

    graph.add_edge(START, "decompose_query")
    graph.add_edge("decompose_query", "parallel_retrieval")
    graph.add_edge("parallel_retrieval", "merge_all_evidence")
    graph.add_edge("merge_all_evidence", "synthesize_report")
    graph.add_edge("synthesize_report", "assemble_report_card")
    graph.add_edge("assemble_report_card", "format_citations")
    graph.add_edge("format_citations", END)
    return graph.compile()
