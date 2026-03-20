from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

try:
    from arq.connections import RedisSettings, create_pool as redis_pool
except Exception:  # pragma: no cover - optional runtime dependency in local test envs
    RedisSettings = None
    redis_pool = None

from backend.config import settings
from backend.crawler.robots import is_allowed
from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/crawl", tags=["crawl"])


class CrawlRequest(BaseModel):
    url: str
    entity_id: str | None = None
    entity_type: str | None = None
    use_browser: bool = False
    priority: int = Field(default=5, ge=1, le=10)


@router.post("")
async def crawl_endpoint(
    payload: CrawlRequest,
    db=Depends(get_db_connection),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    if current_user.auth_method not in ("service", "api_key"):
        raise HTTPException(status_code=403, detail="Crawl endpoint requires service credentials")

    parsed = urlparse(payload.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")

    if not is_allowed(payload.url):
        raise HTTPException(status_code=403, detail="Blocked by robots.txt")

    crawl_id = await db.fetchval(
        """
        INSERT INTO crawl_queue (url, domain, entity_id, entity_type, priority, max_attempts)
        VALUES ($1, $2, $3::uuid, $4::entity_type, $5, $6)
        RETURNING id
        """,
        payload.url,
        parsed.netloc,
        payload.entity_id,
        payload.entity_type,
        payload.priority,
        3,
    )

    estimated_position = await db.fetchval(
        """
        SELECT COUNT(*)::int
        FROM crawl_queue
        WHERE status = 'pending' AND created_at <= NOW()
        """,
    )

    if redis_pool is not None and RedisSettings is not None:
        redis = await redis_pool(RedisSettings.from_dsn(settings.redis_url))
        try:
            await redis.enqueue_job("crawl_task", str(crawl_id))
        finally:
            await redis.aclose()

    return {
        "status": "queued",
        "crawl_id": str(crawl_id),
        "url": payload.url,
        "estimated_position": int(estimated_position or 1),
    }
