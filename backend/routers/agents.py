import asyncio
import json
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from loguru import logger
from sse_starlette.sse import EventSourceResponse

from backend.agents.router import run_agent as run_agent_workflow
from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_current_user
from backend.models.requests import AgentRunRequest
from backend.models.responses import AgentRunResponse
from backend.services.user_service import record_search

router = APIRouter(prefix="/agent", tags=["agents"])


@router.post("/run")
async def run_agent(
    request: AgentRunRequest,
    http_request: Request,
    db=Depends(get_db_connection),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    http_request.state.user_id = current_user.user_id

    recent_runs = await db.fetchval(
        """
        SELECT COUNT(*)
        FROM agent_runs
        WHERE user_id=$1
          AND created_at >= NOW() - INTERVAL '1 minute'
        """,
        current_user.user_id,
    )
    if int(recent_runs or 0) >= 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded for this user")

    run_id = str(uuid4())
    started = time.perf_counter()

    await db.execute(
        """
        INSERT INTO agent_runs (run_id, workflow_name, status, input_payload, user_id)
        VALUES ($1, $2, 'running', $3::jsonb, $4)
        """,
        run_id,
        request.workflow_name,
        request.model_dump_json(),
        current_user.user_id,
    )

    try:
        result = await run_agent_workflow(
            workflow_name=request.workflow_name,
            query=request.query,
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            lead_list=request.lead_list or [],
            run_id=run_id,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
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

        final_response = result.get("final_response", {})
        result_count = 0
        if isinstance(final_response, dict):
            for key in ("people", "facts", "signals", "items"):
                value = final_response.get(key)
                if isinstance(value, list):
                    result_count += len(value)

        await record_search(
            db=db,
            user_id=current_user.user_id,
            query=request.query,
            workflow_name=request.workflow_name,
            agent_run_id=None,
            entity_id=request.entity_id,
            entity_name=None,
            entity_type=request.entity_type,
            result_count=result_count,
        )

        return AgentRunResponse(
            run_id=run_id,
            workflow_name=request.workflow_name,
            status="completed",
            result=final_response,
            steps_log=result.get("steps_log", []),
            citations=result.get("citations", []),
            duration_ms=duration_ms,
        )
    except Exception as exc:
        await db.execute(
            "UPDATE agent_runs SET status='failed', error_message=$2, completed_at=NOW() WHERE run_id=$1",
            run_id,
            str(exc),
        )

        degraded_result = {
            "degraded": True,
            "summary": "Agent providers are temporarily unavailable. Please retry shortly.",
            "error": {
                "code": "AGENT_DEGRADED",
                "message": str(exc),
            },
            "facts": [],
            "people": [],
            "signals": [],
            "citations": [],
        }

        duration_ms = int((time.perf_counter() - started) * 1000)
        await db.execute(
            """
            UPDATE agent_runs
            SET status='completed', output_payload=$2::jsonb, steps_log=$3::jsonb,
                duration_ms=$4, completed_at=NOW(), error_message=$5
            WHERE run_id=$1
            """,
            run_id,
            json.dumps(degraded_result, default=str),
            json.dumps([f"[degraded] {type(exc).__name__}: {exc}"], default=str),
            duration_ms,
            str(exc),
        )

        logger.warning(
            "agent_run_degraded | run_id={} workflow={} error_type={} error={}",
            run_id,
            request.workflow_name,
            type(exc).__name__,
            str(exc),
        )

        return AgentRunResponse(
            run_id=run_id,
            workflow_name=request.workflow_name,
            status="completed",
            result=degraded_result,
            steps_log=[f"[degraded] {type(exc).__name__}: {exc}"],
            citations=[],
            duration_ms=duration_ms,
        )


@router.get("/run/{run_id}")
async def get_agent_run(
    run_id: str,
    db=Depends(get_db_connection),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    row = await db.fetchrow(
        """
        SELECT run_id, workflow_name, status, output_payload, steps_log, duration_ms
        FROM agent_runs
        WHERE run_id=$1
          AND ($2 = 'service' OR user_id=$3)
        """,
        run_id,
        current_user.auth_method,
        current_user.user_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Run not found")

    raw_steps = row["steps_log"]
    steps = raw_steps if isinstance(raw_steps, list) else json.loads(raw_steps) if raw_steps else []
    return AgentRunResponse(
        run_id=str(row["run_id"]),
        workflow_name=str(row["workflow_name"]),
        status=str(row["status"]),
        result=row["output_payload"] if isinstance(row["output_payload"], dict) else None,
        steps_log=steps,
        citations=(row["output_payload"] or {}).get("citations", []) if isinstance(row["output_payload"], dict) else [],
        duration_ms=int(row["duration_ms"] or 0),
    )


@router.get("/run/{run_id}/stream")
async def stream_agent_run(
    run_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db=Depends(get_db_connection),
):
    if current_user.auth_method not in {"service", "api_key", "jwt"}:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    async def event_generator():
        last_index = 0
        for _ in range(60):
            run = await db.fetchrow(
                                """
                                SELECT status, steps_log, output_payload, error_message
                                FROM agent_runs
                                WHERE run_id=$1
                                    AND ($2 = 'service' OR user_id=$3)
                                """,
                run_id,
                                current_user.auth_method,
                                current_user.user_id,
            )

            if not run:
                yield {"event": "error", "data": json.dumps({"error": "not found"})}
                return

            raw_steps = run["steps_log"]
            if isinstance(raw_steps, list):
                steps = raw_steps
            elif raw_steps:
                steps = json.loads(raw_steps)
            else:
                steps = []

            for idx in range(last_index, len(steps)):
                yield {
                    "event": "step",
                    "data": json.dumps({"step": steps[idx], "index": idx}, default=str),
                }
            last_index = len(steps)

            if run["status"] == "completed":
                yield {
                    "event": "done",
                    "data": json.dumps({"status": "completed", "result": run["output_payload"]}, default=str),
                }
                return

            if run["status"] == "failed":
                yield {
                    "event": "done",
                    "data": json.dumps({"status": "failed", "error": run["error_message"]}, default=str),
                }
                return

            await asyncio.sleep(0.5)

        yield {"event": "timeout", "data": json.dumps({"error": "timed out"})}

    return EventSourceResponse(event_generator())
