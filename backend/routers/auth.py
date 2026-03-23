"""Authenticated user profile and personal API key endpoints."""

from datetime import datetime, timedelta, timezone

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from jose import jwt
from passlib.context import CryptContext

from backend.config import settings
from backend.database import get_pool
from backend.middleware.auth import AuthenticatedUser, get_current_user
from backend.models.requests import (
    AuthChangePasswordRequest,
    AuthLoginRequest,
    AuthSignupRequest,
    CreateApiKeyRequest,
    UpdatePreferencesRequest,
)
from backend.services.user_service import create_api_key, update_user_preferences

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def _create_access_token(user_id: str) -> tuple[str, int]:
    expires_in_seconds = max(3600, settings.auth_jwt_expires_hours * 3600)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
    token = jwt.encode(
        {
            "sub": user_id,
            "exp": int(expires_at.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "typ": "access",
        },
        settings.auth_jwt_secret,
        algorithm="HS256",
    )
    return token, expires_in_seconds


def _ensure_auth_configured() -> None:
    if not settings.auth_jwt_secret:
        raise HTTPException(status_code=500, detail="AUTH_JWT_SECRET is not configured")


@router.post("/signup")
async def signup(
    body: AuthSignupRequest,
    pool=Depends(get_pool),
):
    _ensure_auth_configured()
    email = body.email.strip().lower()
    display_name = (body.display_name or "").strip() or email.split("@", 1)[0]
    password_hash = pwd_context.hash(body.password)

    async with pool.acquire() as db:
        try:
            row = await db.fetchrow(
                """
                INSERT INTO users (email, display_name, plan, is_active, auth_provider, password_hash)
                VALUES ($1, $2, 'free', true, 'local', $3)
                RETURNING id, email, display_name, plan, created_at
                """,
                email,
                display_name,
                password_hash,
            )
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
        except (asyncpg.UndefinedColumnError, asyncpg.NotNullViolationError, asyncpg.UndefinedTableError) as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Auth schema is not ready. Run Alembic migrations on the deployed database "
                    "(expected local auth columns on users table)."
                ),
            ) from exc
        except asyncpg.PostgresError as exc:
            raise HTTPException(status_code=503, detail=f"Database auth error: {type(exc).__name__}") from exc

    token, expires_in = _create_access_token(str(row["id"]))
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": str(row["id"]),
            "email": str(row["email"]),
            "display_name": row["display_name"],
            "plan": str(row["plan"]),
            "created_at": row["created_at"],
        },
    }


@router.post("/login")
async def login(
    body: AuthLoginRequest,
    pool=Depends(get_pool),
):
    _ensure_auth_configured()
    email = body.email.strip().lower()

    async with pool.acquire() as db:
        try:
            row = await db.fetchrow(
                """
                SELECT id, email, display_name, plan, created_at, is_active, password_hash
                FROM users
                WHERE email=$1
                """,
                email,
            )
        except (asyncpg.UndefinedColumnError, asyncpg.UndefinedTableError) as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Auth schema is not ready. Run Alembic migrations on the deployed database "
                    "(expected local auth columns on users table)."
                ),
            ) from exc
        except asyncpg.PostgresError as exc:
            raise HTTPException(status_code=503, detail=f"Database auth error: {type(exc).__name__}") from exc

    if row is None or not row["password_hash"] or not row["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token, expires_in = _create_access_token(str(row["id"]))
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": str(row["id"]),
            "email": str(row["email"]),
            "display_name": row["display_name"],
            "plan": str(row["plan"]),
            "created_at": row["created_at"],
        },
    }


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


@router.post("/change-password")
async def change_password(
    body: AuthChangePasswordRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    pool=Depends(get_pool),
):
    async with pool.acquire() as db:
        try:
            row = await db.fetchrow(
                "SELECT password_hash FROM users WHERE id=$1::uuid",
                current_user.user_id,
            )
        except (asyncpg.UndefinedColumnError, asyncpg.UndefinedTableError) as exc:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Auth schema is not ready. Run Alembic migrations on the deployed database "
                    "(expected local auth columns on users table)."
                ),
            ) from exc
        except asyncpg.PostgresError as exc:
            raise HTTPException(status_code=503, detail=f"Database auth error: {type(exc).__name__}") from exc
        if row is None or not row["password_hash"]:
            raise HTTPException(status_code=400, detail="Password login is not available for this account")

        if not pwd_context.verify(body.current_password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Current password is incorrect")

        new_hash = pwd_context.hash(body.new_password)
        await db.execute(
            "UPDATE users SET password_hash=$1, auth_provider='local', updated_at=NOW() WHERE id=$2::uuid",
            new_hash,
            current_user.user_id,
        )

    return {"updated": True}


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
