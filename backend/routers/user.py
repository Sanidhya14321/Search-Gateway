"""Authenticated user data endpoints."""

from fastapi import APIRouter, Depends

from backend.database import get_pool
from backend.middleware.auth import AuthenticatedUser, get_current_user
from backend.models.requests import PaginationParams, SaveEntityRequest, UpdateSavedEntityRequest
from backend.services.user_service import get_saved_entities, get_search_history, save_entity, update_saved_entity

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/history")
async def search_history(
    pagination: PaginationParams = Depends(),
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        return await get_search_history(
            db,
            current_user.user_id,
            pagination.limit,
            pagination.offset,
        )


@router.get("/saved")
async def saved_entities(
    pagination: PaginationParams = Depends(),
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        return await get_saved_entities(
            db,
            current_user.user_id,
            pagination.limit,
            pagination.offset,
        )


@router.post("/saved")
async def bookmark_entity(
    body: SaveEntityRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        return await save_entity(
            db,
            current_user.user_id,
            body.entity_id,
            body.entity_type,
            body.entity_name,
            body.note,
            body.tags,
        )


@router.delete("/saved/{entity_id}")
async def remove_bookmark(
    entity_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        await db.execute(
            """
            DELETE FROM user_saved_entities
            WHERE user_id=$1::uuid AND entity_id=$2::uuid
            """,
            current_user.user_id,
            entity_id,
        )
    return {"removed": True}


@router.patch("/saved/{entity_id}")
async def update_bookmark(
    entity_id: str,
    body: UpdateSavedEntityRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        result = await update_saved_entity(
            db=db,
            user_id=current_user.user_id,
            entity_id=entity_id,
            entity_name=body.entity_name,
            note=body.note,
            tags=body.tags,
        )
    return result


@router.get("/enrichment-jobs")
async def enrichment_jobs(
    pagination: PaginationParams = Depends(),
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        total = int(
            await db.fetchval(
                "SELECT COUNT(*) FROM user_enrichment_jobs WHERE user_id=$1::uuid",
                current_user.user_id,
            )
            or 0
        )
        rows = await db.fetch(
            """
            SELECT id, job_name, status, input_row_count, output_row_count,
                   flagged_count, created_at, completed_at
            FROM user_enrichment_jobs
            WHERE user_id=$1::uuid
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            current_user.user_id,
            pagination.limit,
            pagination.offset,
        )

    items = [dict(row) for row in rows]
    return {
        "items": items,
        "total": total,
        "limit": pagination.limit,
        "offset": pagination.offset,
        "has_more": (pagination.offset + len(items)) < total,
    }
