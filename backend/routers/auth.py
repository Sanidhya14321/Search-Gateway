"""Authenticated user profile and personal API key endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.database import get_pool
from backend.middleware.auth import AuthenticatedUser, get_current_user
from backend.models.requests import CreateApiKeyRequest, UpdatePreferencesRequest
from backend.services.user_service import create_api_key, update_user_preferences

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        row = await db.fetchrow(
            """
            SELECT id, email, display_name, avatar_url, plan, preferences, created_at
            FROM users
            WHERE id=$1::uuid
            """,
            current_user.user_id,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)


@router.patch("/me")
async def update_me(
    body: UpdatePreferencesRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        updated_prefs = await update_user_preferences(db, current_user.user_id, body.preferences or {})
        if body.display_name:
            await db.execute(
                "UPDATE users SET display_name=$1, updated_at=NOW() WHERE id=$2::uuid",
                body.display_name,
                current_user.user_id,
            )
    return {"updated": True, "preferences": updated_prefs}


@router.get("/api-keys")
async def list_api_keys(
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT id, key_prefix, name, last_used_at, expires_at, is_active, created_at
            FROM user_api_keys
            WHERE user_id=$1::uuid AND is_active=true
            ORDER BY created_at DESC
            """,
            current_user.user_id,
        )
    return {"api_keys": [dict(row) for row in rows]}


@router.post("/api-keys")
async def create_personal_api_key(
    body: CreateApiKeyRequest | None = None,
    name: str | None = Query(default=None, min_length=1, max_length=255),
    expires_in_days: int | None = Query(default=None, ge=1, le=365),
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    key_name = body.name if body else name
    key_expires = body.expires_in_days if body else expires_in_days
    if not key_name:
        raise HTTPException(status_code=400, detail="API key name is required")

    async with pool.acquire() as db:
        return await create_api_key(
            db,
            current_user.user_id,
            name=key_name,
            expires_in_days=key_expires,
        )


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        result = await db.execute(
            """
            UPDATE user_api_keys
            SET is_active=false
            WHERE id=$1::uuid AND user_id=$2::uuid
            """,
            key_id,
            current_user.user_id,
        )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="API key not found")
    return {"revoked": True}
