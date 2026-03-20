import json
import time
from collections.abc import Sequence
from uuid import uuid4

from backend.agents.account_brief import build_account_brief_graph
from backend.agents.crm_enrichment import build_crm_enrichment_graph
from backend.agents.lead_finder import build_lead_finder_graph
from backend.agents.llm_client import llm_json_call_with_fallback
from backend.agents.ops_debug import build_ops_debug_graph
from backend.agents.research import build_research_graph
from backend.agents.state import CRMindState
from backend.database import get_pool
from backend.config import settings
from backend.services.query_cache import get_cached, make_query_hash, set_cached

WORKFLOW_REGISTRY: dict[str, object] = {
    "lead_finder": build_lead_finder_graph(),
    "account_brief": build_account_brief_graph(),
    "crm_enrichment": build_crm_enrichment_graph(),
    "research": build_research_graph(),
    "ops_debug": build_ops_debug_graph(),
}


def serialize_steps(steps: list) -> str:
    """Serialize steps_log to JSON string, handling non-serializable types."""
    return json.dumps(steps, default=str)


def parse_steps(raw: object) -> list:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str) and raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
    return []


async def persist_steps(db, run_id: str, steps: Sequence[object]) -> None:
    await db.execute(
        "UPDATE agent_runs SET steps_log=$1 WHERE run_id=$2",
        serialize_steps(list(steps)),
        run_id,
    )


async def classify_intent(query: str) -> str:
    text = query.lower()
    if "find" in text and " at " in text or "people at" in text or "engineers at" in text:
        return "lead_finder"
    if "brief" in text or "signals" in text or "hiring" in text or "summary" in text:
        return "account_brief"
    if "enrich" in text or "csv" in text or "lead list" in text:
        return "crm_enrichment"
    if "research" in text or "market" in text or "landscape" in text:
        return "research"
    if "why" in text or "stale" in text or "failed" in text or "debug" in text:
        return "ops_debug"

    classified = await llm_json_call_with_fallback(
        f"Classify query into one of: {','.join(WORKFLOW_REGISTRY.keys())}. Return JSON with key workflow_name. Query: {query}"
    )
    return str(classified.get("workflow_name", "research"))


async def run_agent(workflow_name: str, query: str, **kwargs) -> CRMindState:
    selected_workflow = workflow_name if workflow_name in WORKFLOW_REGISTRY else await classify_intent(query)
    graph = WORKFLOW_REGISTRY[selected_workflow]

    initial_state: CRMindState = {
        "query": query,
        "entity_id": kwargs.get("entity_id"),
        "entity_type": kwargs.get("entity_type"),
        "lead_list": kwargs.get("lead_list", []),
        "resolved_entity": None,
        "resolution_confidence": 0.0,
        "retrieved_chunks": [],
        "ranked_chunks": [],
        "tool_calls": [],
        "steps_log": [],
        "iteration_count": 0,
        "final_response": None,
        "citations": [],
        "error": None,
    }

    run_id = str(kwargs.get("run_id") or uuid4())
    pool = await get_pool()
    started = time.perf_counter()
    async with pool.acquire() as db:
        query_hash = make_query_hash(query, selected_workflow)
        cached = await get_cached(query_hash, db)
        if cached is not None:
            return {
                **initial_state,
                "final_response": cached,
                "cache_hit": True,
                "steps_log": ["[cache] hit"],
                "citations": cached.get("citations", []) if isinstance(cached, dict) else [],
            }

        await db.execute(
            """
            INSERT INTO agent_runs (run_id, workflow_name, status, input_payload, trace_id)
            VALUES ($1, $2, 'running', $3::jsonb, $4)
            ON CONFLICT (run_id) DO NOTHING
            """,
            run_id,
            selected_workflow,
            json.dumps({"query": query, **kwargs}, default=str),
            kwargs.get("trace_id"),
        )

    try:
        result = await graph.ainvoke(initial_state)
        duration_ms = int((time.perf_counter() - started) * 1000)

        async with pool.acquire() as db:
            await set_cached(
                query_hash=query_hash,
                query_text=query,
                workflow_name=selected_workflow,
                response=result.get("final_response", {}),
                ttl_seconds=settings.cache_ttl_seconds,
                db=db,
            )
            await db.execute(
                """
                UPDATE agent_runs
                SET status='completed', output_payload=$2::jsonb, steps_log=$3::jsonb,
                    duration_ms=$4, completed_at=NOW()
                WHERE run_id=$1
                """,
                run_id,
                json.dumps(result.get("final_response", {}), default=str),
                json.dumps(result.get("steps_log", []), default=str),
                duration_ms,
            )
        return result
    except Exception as exc:
        async with pool.acquire() as db:
            await db.execute(
                "UPDATE agent_runs SET status='failed', error_message=$2, completed_at=NOW() WHERE run_id=$1",
                run_id,
                str(exc),
            )
        raise
