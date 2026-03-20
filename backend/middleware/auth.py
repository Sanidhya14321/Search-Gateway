"""JWT and API key authentication dependencies for CRMind."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import asyncpg
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext

from backend.config import settings
from backend.database import get_pool
from backend.middleware.trace import get_trace_id

bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class AuthenticatedUser:
    user_id: str
    supabase_user_id: str
    email: str
    plan: str
    auth_method: str


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    pool: asyncpg.Pool = Depends(get_pool),
) -> AuthenticatedUser:
    trace = get_trace_id()

    if credentials and credentials.scheme.lower() == "bearer":
        try:
            return await _verify_jwt(credentials.credentials, pool, trace)
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("jwt_error | trace_id={} error={}", trace, type(exc).__name__)
            raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    if api_key:
        if api_key == settings.internal_service_api_key:
            return AuthenticatedUser(
                user_id="service",
                supabase_user_id="service",
                email="service@internal",
                plan="admin",
                auth_method="service",
            )
        return await _verify_api_key(api_key, pool, trace)

    raise HTTPException(
        status_code=401,
        detail="Authentication required. Provide a Bearer token or X-API-Key header.",
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    pool: asyncpg.Pool = Depends(get_pool),
) -> Optional[AuthenticatedUser]:
    try:
        return await get_current_user(credentials=credentials, api_key=api_key, pool=pool)
    except HTTPException:
        return None


async def _verify_jwt(token: str, pool: asyncpg.Pool, trace: str) -> AuthenticatedUser:
    if not settings.supabase_jwt_secret:
        raise HTTPException(status_code=401, detail="JWT auth is not configured")

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        logger.warning("jwt_decode_failed | trace_id={} error={}", trace, str(exc))
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    supabase_user_id = payload.get("sub")
    if not supabase_user_id:
        raise HTTPException(status_code=401, detail="Token missing sub claim")

    async with pool.acquire() as db:
        user = await db.fetchrow(
            "SELECT id, email, plan FROM users WHERE supabase_user_id=$1 AND is_active=true",
            supabase_user_id,
        )

    if user is None:
        async with pool.acquire() as db:
            user = await _provision_user(db, payload, supabase_user_id)

    logger.info("auth_jwt | trace_id={} user_id={} plan={}", trace, user["id"], user["plan"])
    return AuthenticatedUser(
        user_id=str(user["id"]),
        supabase_user_id=str(supabase_user_id),
        email=str(user["email"]),
        plan=str(user["plan"]),
        auth_method="jwt",
    )


async def _provision_user(db: asyncpg.Connection, payload: dict, supabase_user_id: str) -> asyncpg.Record:
    email = str(payload.get("email", "")).strip()
    if not email:
        email = f"{supabase_user_id}@supabase.local"

    user_meta = payload.get("user_metadata") or {}
    display_name = (
        user_meta.get("full_name")
        or user_meta.get("name")
        or email.split("@", 1)[0]
    )

    return await db.fetchrow(
        """
        INSERT INTO users (supabase_user_id, email, display_name, plan)
        VALUES ($1::uuid, $2, $3, 'free')
        ON CONFLICT (supabase_user_id) DO UPDATE
            SET email = EXCLUDED.email,
                updated_at = NOW()
        RETURNING id, email, plan
        """,
        supabase_user_id,
        email,
        display_name,
    )


async def _verify_api_key(raw_key: str, pool: asyncpg.Pool, trace: str) -> AuthenticatedUser:
    if not raw_key.startswith(settings.api_key_prefix):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    key_prefix = raw_key[: len(settings.api_key_prefix) + 8]

    async with pool.acquire() as db:
        rows = await db.fetch(
            """
            SELECT
                k.id,
                k.key_hash,
                k.is_active,
                k.expires_at,
                u.id AS user_id,
                u.email,
                u.plan,
                u.supabase_user_id
            FROM user_api_keys k
            JOIN users u ON u.id = k.user_id
            WHERE k.key_prefix = $1
            """,
            key_prefix,
        )

    now = datetime.now(timezone.utc)
    for row in rows:
        if not row["is_active"]:
            continue
        expires_at = row["expires_at"]
        if expires_at is not None:
            expires_at = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
            if expires_at < now:
                continue

        if pwd_context.verify(raw_key, row["key_hash"]):
            async with pool.acquire() as db:
                await db.execute(
                    "UPDATE user_api_keys SET last_used_at=NOW() WHERE id=$1",
                    row["id"],
                )
            logger.info("auth_api_key | trace_id={} user_id={} key_prefix={}", trace, row["user_id"], key_prefix)
            return AuthenticatedUser(
                user_id=str(row["user_id"]),
                supabase_user_id=str(row["supabase_user_id"]),
                email=str(row["email"]),
                plan=str(row["plan"]),
                auth_method="api_key",
            )

    raise HTTPException(status_code=401, detail="Invalid or expired API key")
