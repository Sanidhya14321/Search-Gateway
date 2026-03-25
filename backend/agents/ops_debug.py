from urllib.parse import urlparse

from backend.agents.graph_runtime import END, START, StateGraph

from backend.agents.llm_client import llm_json_call_with_fallback
from backend.agents.state import CRMindState
from backend.database import get_pool


async def identify_subject_node(state: CRMindState) -> dict:
    query = state.get("query", "")
    domain = ""
    if "http" in query:
        try:
            domain = urlparse(query).netloc
        except Exception:
            domain = ""
    return {
        "subject": {"entity_id": state.get("entity_id"), "domain": domain},
        "steps_log": state.get("steps_log", []) + ["[identify_subject] complete"],
    }


async def inspect_freshness_node(state: CRMindState) -> dict:
    entity_id = state.get("entity_id")
    if not entity_id:
        return {"freshness": None, "steps_log": state.get("steps_log", []) + ["[inspect_freshness] no entity"]}

    pool = await get_pool()
    async with pool.acquire() as db:
        row = await db.fetchrow(
            "SELECT freshness_score, updated_at FROM companies WHERE id=$1::uuid",
            entity_id,
        )
    return {"freshness": dict(row) if row else None, "steps_log": state.get("steps_log", []) + ["[inspect_freshness] done"]}


async def check_crawl_queue_node(state: CRMindState) -> dict:
    pool = await get_pool()
    subject = state.get("subject", {})
    domain = subject.get("domain")
    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT status, attempts, error_message
            FROM crawl_queue
            WHERE ($1::text = '' OR domain=$1)
            ORDER BY created_at DESC
            LIMIT 10
            """,
            domain or "",
        )
    return {"crawl_queue": [dict(row) for row in rows], "steps_log": state.get("steps_log", []) + ["[check_crawl_queue] done"]}


async def inspect_pipeline_logs_node(state: CRMindState) -> dict:
    pool = await get_pool()
    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT run_id, workflow_name, status, error_message, created_at
            FROM agent_runs
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
    return {"pipeline_logs": [dict(row) for row in rows], "steps_log": state.get("steps_log", []) + ["[inspect_pipeline_logs] done"]}


async def identify_failure_cause_node(state: CRMindState) -> dict:
    prompt = (
        "Classify likely failure type from logs into one of: ingestion, retrieval, synthesis, unknown.\n"
        f"Queue: {state.get('crawl_queue', [])}\n"
        f"Agent logs: {state.get('pipeline_logs', [])}"
    )
    try:
        result = await llm_json_call_with_fallback(prompt)
    except Exception:
        result = {
            "failure_type": "unknown",
            "reason": "LLM unavailable during diagnostics classification",
            "degraded": True,
        }
    return {"failure_cause": result, "steps_log": state.get("steps_log", []) + ["[identify_failure_cause] done"]}


async def generate_remediation_node(state: CRMindState) -> dict:
    prompt = (
        "Suggest remediation as JSON with keys remediation and auto_fixable (bool).\n"
        f"Failure: {state.get('failure_cause', {})}"
    )
    try:
        remediation = await llm_json_call_with_fallback(prompt)
    except Exception:
        remediation = {
            "remediation": [
                "Retry the request after 30-60 seconds.",
                "Check backend health endpoint and trace logs.",
                "Verify CORS and API key/JWT authentication headers.",
            ],
            "auto_fixable": False,
            "degraded": True,
        }
    return {
        "final_response": remediation,
        "steps_log": state.get("steps_log", []) + ["[generate_remediation] done"],
    }


def build_ops_debug_graph():
    graph = StateGraph(CRMindState)
    graph.add_node("identify_subject", identify_subject_node)
    graph.add_node("inspect_freshness", inspect_freshness_node)
    graph.add_node("check_crawl_queue", check_crawl_queue_node)
    graph.add_node("inspect_pipeline_logs", inspect_pipeline_logs_node)
    graph.add_node("identify_failure_cause", identify_failure_cause_node)
    graph.add_node("generate_remediation", generate_remediation_node)

    graph.add_edge(START, "identify_subject")
    graph.add_edge("identify_subject", "inspect_freshness")
    graph.add_edge("inspect_freshness", "check_crawl_queue")
    graph.add_edge("check_crawl_queue", "inspect_pipeline_logs")
    graph.add_edge("inspect_pipeline_logs", "identify_failure_cause")
    graph.add_edge("identify_failure_cause", "generate_remediation")
    graph.add_edge("generate_remediation", END)
    return graph.compile()
