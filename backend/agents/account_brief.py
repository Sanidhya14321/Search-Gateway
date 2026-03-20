from backend.agents.graph_runtime import END, START, StateGraph

from backend.agents.nodes.format_citations import format_citations_node
from backend.agents.nodes.rank_results import rank_results_node
from backend.agents.nodes.resolve_entity import resolve_entity_node
from backend.agents.nodes.synthesize import synthesize_node
from backend.agents.nodes.vector_search_node import vector_search_node
from backend.agents.state import CRMindState
from backend.database import get_pool


async def fetch_signals_node(state: CRMindState) -> dict:
    entity_id = state.get("entity_id")
    if not entity_id:
        return {"signals": [], "steps_log": state.get("steps_log", []) + ["[fetch_signals] no entity"]}

    pool = await get_pool()
    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT signal_type, description, confidence, source_url, detected_at
            FROM signals
            WHERE entity_id=$1::uuid
              AND detected_at > NOW() - INTERVAL '90 days'
            ORDER BY detected_at DESC
            LIMIT 25
            """,
            entity_id,
        )
    signals = [dict(row) for row in rows]
    return {"signals": signals, "steps_log": state.get("steps_log", []) + [f"[fetch_signals] count={len(signals)}"]}


async def fetch_people_changes_node(state: CRMindState) -> dict:
    entity_id = state.get("entity_id")
    if not entity_id:
        return {"people_changes": [], "steps_log": state.get("steps_log", []) + ["[fetch_people_changes] no entity"]}

    pool = await get_pool()
    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT p.full_name, r.title, r.start_date
            FROM people p
            JOIN roles r ON r.person_id = p.id
            WHERE r.company_id=$1::uuid
              AND r.start_date > NOW() - INTERVAL '180 days'
            ORDER BY r.start_date DESC
            LIMIT 25
            """,
            entity_id,
        )

    changes = [dict(row) for row in rows]
    return {"people_changes": changes, "steps_log": state.get("steps_log", []) + [f"[fetch_people_changes] count={len(changes)}"]}


async def synthesize_brief_node(state: CRMindState) -> dict:
    base = await synthesize_node(state)
    response = base.get("final_response", {})
    response.setdefault("signal_timeline", state.get("signals", []))
    response.setdefault("key_people", state.get("people_changes", []))
    response.setdefault("why_reach_out_now", "Explain why this matters for a sales team reaching out to this account.")
    return {
        "final_response": response,
        "steps_log": base.get("steps_log", []) + ["[synthesize_brief] built account brief fields"],
    }


def build_account_brief_graph():
    graph = StateGraph(CRMindState)
    graph.add_node("resolve_entity", resolve_entity_node)
    graph.add_node("fetch_signals", fetch_signals_node)
    graph.add_node("fetch_people_changes", fetch_people_changes_node)
    graph.add_node("vector_search", vector_search_node)
    graph.add_node("rank_results", rank_results_node)
    graph.add_node("synthesize_brief", synthesize_brief_node)
    graph.add_node("format_citations", format_citations_node)

    graph.add_edge(START, "resolve_entity")
    graph.add_edge("resolve_entity", "fetch_signals")
    graph.add_edge("fetch_signals", "fetch_people_changes")
    graph.add_edge("fetch_people_changes", "vector_search")
    graph.add_edge("vector_search", "rank_results")
    graph.add_edge("rank_results", "synthesize_brief")
    graph.add_edge("synthesize_brief", "format_citations")
    graph.add_edge("format_citations", END)
    return graph.compile()
