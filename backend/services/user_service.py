"""Database operations for user-owned records."""

import json
import secrets
import string
from datetime import datetime, timedelta, timezone

import asyncpg
from passlib.context import CryptContext

from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _generate_api_key() -> tuple[str, str, str]:
    alphabet = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(alphabet) for _ in range(settings.api_key_length))
    raw_key = f"{settings.api_key_prefix}{random_part}"
    key_hash = pwd_context.hash(raw_key)
    key_prefix = raw_key[: len(settings.api_key_prefix) + 8]
    return raw_key, key_hash, key_prefix


async def create_api_key(
    db: asyncpg.Connection,
    user_id: str,
    name: str,
    expires_in_days: int | None = None,
) -> dict:
    raw_key, key_hash, key_prefix = _generate_api_key()
    expires_at = None
    if expires_in_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    row = await db.fetchrow(
        """
        INSERT INTO user_api_keys (user_id, key_hash, key_prefix, name, expires_at)
        VALUES ($1::uuid, $2, $3, $4, $5)
        RETURNING id, key_prefix, name, created_at, expires_at
        """,
        user_id,
        key_hash,
        key_prefix,
        name,
        expires_at,
    )

    return {
        "id": str(row["id"]),
        "raw_key": raw_key,
        "key_prefix": str(row["key_prefix"]),
        "name": str(row["name"]),
        "created_at": row["created_at"].isoformat(),
        "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
        "warning": "Save this key now. It will not be shown again.",
    }


async def record_search(
    db: asyncpg.Connection,
    user_id: str,
    query: str,
    workflow_name: str | None,
    agent_run_id: str | None,
    entity_id: str | None,
    entity_name: str | None,
    entity_type: str | None,
    result_count: int,
) -> None:
    await db.execute(
        """
        INSERT INTO user_search_history
          (user_id, query, workflow_name, agent_run_id,
           entity_id, entity_type, entity_name, result_count)
        VALUES ($1::uuid, $2, $3, $4::uuid, $5::uuid, $6, $7, $8)
        """,
        user_id,
        query,
        workflow_name,
        agent_run_id,
        entity_id,
        entity_type,
        entity_name,
        result_count,
    )


async def save_entity(
    db: asyncpg.Connection,
    user_id: str,
    entity_id: str,
    entity_type: str,
    entity_name: str,
    note: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    row = await db.fetchrow(
        """
        INSERT INTO user_saved_entities
          (user_id, entity_id, entity_type, entity_name, note, tags)
        VALUES ($1::uuid, $2::uuid, $3::entity_type, $4, $5, $6::text[])
        ON CONFLICT (user_id, entity_id) DO UPDATE
            SET note = EXCLUDED.note,
                tags = EXCLUDED.tags
        RETURNING id, created_at
        """,
        user_id,
        entity_id,
        entity_type,
        entity_name,
        note,
        tags or [],
    )
    return {"id": str(row["id"]), "saved_at": row["created_at"].isoformat()}


async def get_saved_entities(
    db: asyncpg.Connection,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    total = int(
        await db.fetchval(
            "SELECT COUNT(*) FROM user_saved_entities WHERE user_id=$1::uuid",
            user_id,
        )
        or 0
    )
    rows = await db.fetch(
        """
        SELECT entity_id, entity_type, entity_name, note, tags, created_at
        FROM user_saved_entities
        WHERE user_id=$1::uuid
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
        """,
        user_id,
        limit,
        offset,
    )
    items = [dict(row) for row in rows]
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(items)) < total,
    }


async def get_search_history(
    db: asyncpg.Connection,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    total = int(
        await db.fetchval(
            "SELECT COUNT(*) FROM user_search_history WHERE user_id=$1::uuid",
            user_id,
        )
        or 0
    )
    rows = await db.fetch(
        """
        SELECT query, workflow_name, entity_name, entity_type, result_count, created_at
        FROM user_search_history
        WHERE user_id=$1::uuid
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
        """,
        user_id,
        limit,
        offset,
    )
    items = [dict(row) for row in rows]
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(items)) < total,
    }


async def update_user_preferences(db: asyncpg.Connection, user_id: str, preferences: dict) -> dict:
    row = await db.fetchrow(
        """
        UPDATE users
        SET preferences = preferences || $1::jsonb,
            updated_at = NOW()
        WHERE id=$2::uuid
        RETURNING preferences
        """,
        json.dumps(preferences),
        user_id,
    )
    return dict(row["preferences"] if row else {})
