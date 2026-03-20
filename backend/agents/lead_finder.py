from backend.agents.graph_runtime import END, START, StateGraph

from backend.agents.nodes.format_citations import format_citations_node
from backend.agents.nodes.parse_query import parse_query_node
from backend.agents.nodes.rank_results import rank_results_node
from backend.agents.nodes.resolve_entity import resolve_entity_node
from backend.agents.nodes.synthesize import synthesize_node
from backend.agents.nodes.vector_search_node import vector_search_node
from backend.agents.state import CRMindState
from backend.database import get_pool


async def search_people_db_node(state: CRMindState) -> dict:
    entity_id = state.get("entity_id")
    if not entity_id:
        return {"db_people_results": [], "steps_log": state.get("steps_log", []) + ["[search_people_db] no entity"]}

    parsed = state.get("_parsed_filters", {})
    seniority = parsed.get("seniority")
    title_keywords = parsed.get("title_keywords") or []
    title_patterns = [f"%{keyword}%" for keyword in title_keywords]

    pool = await get_pool()
    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT p.id, p.canonical_id, p.full_name, p.current_title, p.seniority_level
            FROM people p
            LEFT JOIN roles r ON r.person_id = p.id
            WHERE p.current_company_id = $1::uuid
              AND ($2::seniority_level IS NULL OR p.seniority_level = $2::seniority_level)
              AND (
                cardinality($3::text[]) = 0
                OR p.current_title ILIKE ANY($3::text[])
                OR r.title ILIKE ANY($3::text[])
              )
            LIMIT 50
            """,
            entity_id,
            seniority,
            title_patterns,
        )

    people = [dict(row) for row in rows]
    return {
        "db_people_results": people,
        "steps_log": state.get("steps_log", []) + [f"[search_people_db] people={len(people)}"],
    }


async def merge_dedup_node(state: CRMindState) -> dict:
    seen: set[str] = set()
    merged_chunks = list(state.get("retrieved_chunks", []))
    for person in state.get("db_people_results", []):
        person_id = str(person.get("canonical_id") or person.get("id"))
        if person_id in seen:
            continue
        seen.add(person_id)
        merged_chunks.append(
            {
                "id": f"person_{person_id}",
                "chunk_text": f"{person.get('full_name', '')} {person.get('current_title', '')}",
                "source_doc_id": "",
                "entity_id": state.get("entity_id"),
                "source_url": "",
                "source_type": "database",
                "fetched_at": None,
                "similarity": 0.65,
                "freshness_score": 0.7,
                "trust_score": 0.9,
                "final_score": 0.0,
                "retrieval_source": "db",
            }
        )

    return {
        "retrieved_chunks": merged_chunks,
        "steps_log": state.get("steps_log", []) + [f"[merge_dedup] merged={len(merged_chunks)}"],
    }


async def verify_sources_node(state: CRMindState) -> dict:
    verified = [chunk for chunk in state.get("retrieved_chunks", []) if chunk.get("source_url") or chunk.get("source_type") == "database"]
    return {
        "retrieved_chunks": verified,
        "steps_log": state.get("steps_log", []) + [f"[verify_sources] verified={len(verified)}"],
    }


def _resolution_gate(state: CRMindState) -> str:
    return "found" if float(state.get("resolution_confidence", 0.0)) >= 0.6 else "not_found"


async def _entity_not_found_node(state: CRMindState) -> dict:
    return {
        "error": "Entity not resolved",
        "final_response": {"summary": "Entity resolution failed", "people": [], "facts": [], "signals": [], "degraded": True},
        "steps_log": state.get("steps_log", []) + ["[resolve_company] confidence below threshold"],
    }


def build_lead_finder_graph():
    graph = StateGraph(CRMindState)

    graph.add_node("parse_query", parse_query_node)
    graph.add_node("resolve_company", resolve_entity_node)
    graph.add_node("search_people_db", search_people_db_node)
    graph.add_node("vector_search", vector_search_node)
    graph.add_node("merge_dedup", merge_dedup_node)
    graph.add_node("verify_sources", verify_sources_node)
    graph.add_node("rank_results", rank_results_node)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("format_citations", format_citations_node)
    graph.add_node("entity_not_found", _entity_not_found_node)

    graph.add_edge(START, "parse_query")
    graph.add_edge("parse_query", "resolve_company")
    graph.add_conditional_edges(
        "resolve_company",
        _resolution_gate,
        {
            "found": "search_people_db",
            "not_found": "entity_not_found",
        },
    )
    graph.add_edge("entity_not_found", END)
    graph.add_edge("search_people_db", "vector_search")
    graph.add_edge("vector_search", "merge_dedup")
    graph.add_edge("merge_dedup", "verify_sources")
    graph.add_edge("verify_sources", "rank_results")
    graph.add_edge("rank_results", "synthesize")
    graph.add_edge("synthesize", "format_citations")
    graph.add_edge("format_citations", END)

    return graph.compile()
