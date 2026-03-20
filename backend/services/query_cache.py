import hashlib
import json


async def get_cached(query_hash: str, db):
    row = await db.fetchrow(
        """
        SELECT id, response_json
        FROM query_cache
        WHERE query_hash=$1
          AND expires_at > NOW()
        """,
        query_hash,
    )
    if row is None:
        return None

    await db.execute("UPDATE query_cache SET hit_count = hit_count + 1 WHERE id=$1::uuid", row["id"])
    payload = row["response_json"]
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str) and payload:
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return None
    return None


async def set_cached(
    query_hash: str,
    query_text: str,
    workflow_name: str,
    response: dict,
    ttl_seconds: int,
    db,
):
    await db.execute(
        """
        INSERT INTO query_cache (query_hash, query_text, workflow_name, response_json, expires_at)
        VALUES ($1, $2, $3, $4::jsonb, NOW() + make_interval(secs => $5))
        ON CONFLICT (query_hash)
        DO UPDATE SET
          response_json=EXCLUDED.response_json,
          workflow_name=EXCLUDED.workflow_name,
          expires_at=EXCLUDED.expires_at,
          hit_count=query_cache.hit_count + 1
        """,
        query_hash,
        query_text,
        workflow_name,
        json.dumps(response, default=str),
        ttl_seconds,
    )
    return None


def make_query_hash(query: str, workflow_name: str) -> str:
    payload = f"{workflow_name}:{query}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
