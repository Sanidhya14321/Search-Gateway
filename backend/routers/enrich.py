import asyncio
import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.agents.router import run_agent
from backend.database import get_pool
from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/enrich", tags=["enrich"])


class EnrichRequest(BaseModel):
    name: str | None = None
    domain: str | None = None
    title: str | None = None


class BatchEnrichRequest(BaseModel):
    leads: list[dict] = Field(default_factory=list, max_length=500)


@router.post("")
async def enrich_endpoint(
    request: EnrichRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    query = request.name or request.domain
    if not query:
        raise HTTPException(status_code=400, detail="name or domain is required")

    lead = {"name": request.name, "company": request.domain or request.name, "title": request.title}
    result = await run_agent("crm_enrichment", f"enrich single lead {query}", lead_list=[lead])
    return {
        "status": "completed",
        "result": result.get("final_response", {}),
        "user_id": current_user.user_id,
    }


@router.post("/batch")
async def enrich_batch(
    request: BatchEnrichRequest,
    db=Depends(get_db_connection),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    if not request.leads:
        raise HTTPException(status_code=400, detail="leads required")
    if any(not (lead.get("name") or lead.get("domain") or lead.get("company")) for lead in request.leads):
        raise HTTPException(status_code=400, detail="each lead must include at least one of name/domain/company")

    job_id = str(uuid4())
    await db.execute(
        """
        INSERT INTO agent_runs (run_id, workflow_name, status, input_payload)
        VALUES ($1, 'crm_enrichment', 'running', $2::jsonb)
        """,
        job_id,
        json.dumps({"leads": request.leads}, default=str),
    )

    enrichment_job_id = await db.fetchval(
        """
        INSERT INTO user_enrichment_jobs (
            user_id,
            job_name,
            agent_run_id,
            status,
            input_row_count
        )
        SELECT $1::uuid, $2, id, 'processing', $3
        FROM agent_runs
        WHERE run_id = $4
        RETURNING id
        """,
        current_user.user_id,
        "Batch enrichment",
        len(request.leads),
        job_id,
    )

    async def _persist_job() -> None:
        try:
            from inspect import isawaitable
            result = await run_agent("crm_enrichment", "batch enrichment", lead_list=request.leads, run_id=job_id)
            pool_candidate = get_pool()
            # Handle both async get_pool() (normal) and sync monkeypatches in tests
            if isawaitable(pool_candidate):
                pool = await pool_candidate
            else:
                pool = pool_candidate
            
            # Fallback: if pool is None, create it
            if pool is None:
                from backend.database import create_pool
                pool = await create_pool()
            
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE agent_runs SET status='completed', output_payload=$2::jsonb, completed_at=NOW() WHERE run_id=$1",
                    job_id,
                    json.dumps(result.get("final_response", {}), default=str),
                )
                await conn.execute(
                    """
                    UPDATE user_enrichment_jobs
                    SET status='completed',
                        output_row_count=$2,
                        flagged_count=$3,
                        output_data=$4::jsonb,
                        completed_at=NOW()
                    WHERE id=$1::uuid
                    """,
                    enrichment_job_id,
                    len((result.get("final_response") or {}).get("items", [])) if isinstance(result.get("final_response"), dict) else 0,
                    len((result.get("final_response") or {}).get("flagged", [])) if isinstance(result.get("final_response"), dict) else 0,
                    json.dumps(result.get("final_response", {}), default=str),
                )
        except Exception as exc:
            from inspect import isawaitable
            pool_candidate = get_pool()
            # Handle both async get_pool() (normal) and sync monkeypatches in tests
            if isawaitable(pool_candidate):
                pool = await pool_candidate
            else:
                pool = pool_candidate
            
            # Fallback: if pool is None, create it
            if pool is None:
                from backend.database import create_pool
                pool = await create_pool()
            
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE agent_runs SET status='failed', error_message=$2, completed_at=NOW() WHERE run_id=$1",
                    job_id,
                    str(exc),
                )
                await conn.execute(
                    """
                    UPDATE user_enrichment_jobs
                    SET status='failed',
                        error_message=$2,
                        completed_at=NOW()
                    WHERE id=$1::uuid
                    """,
                    enrichment_job_id,
                    str(exc),
                )

    asyncio.create_task(_persist_job())

    return {
        "job_id": job_id,
        "user_job_id": str(enrichment_job_id),
        "status": "processing",
        "total_leads": len(request.leads),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/batch/{job_id}")
async def enrich_batch_status(
    job_id: str,
    db=Depends(get_db_connection),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    row = await db.fetchrow(
        """
        SELECT ar.status, ar.output_payload, ar.error_message
        FROM agent_runs ar
        JOIN user_enrichment_jobs uj ON uj.agent_run_id = ar.id
        WHERE ar.run_id=$1
          AND ar.workflow_name='crm_enrichment'
          AND uj.user_id=$2::uuid
        """,
        job_id,
        current_user.user_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="job not found")

    status = str(row["status"])
    payload = row["output_payload"]
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"raw": payload}

    if status == "completed":
        return {"job_id": job_id, "status": "completed", "result": payload}
    if status == "failed":
        return {"job_id": job_id, "status": "failed", "error": row["error_message"]}
    return {"job_id": job_id, "status": "processing", "progress_hint": "batch enrichment is running"}
