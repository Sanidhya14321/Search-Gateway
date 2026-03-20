from fastapi import APIRouter, Depends, Query

from backend.dependencies import get_db_connection
from backend.middleware.auth import AuthenticatedUser, get_current_user
from backend.models.responses import PaginatedResponse

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/{entity_id}")
async def list_signals(
    entity_id: str,
    signal_type: str | None = Query(default=None),
    days_back: int = Query(default=90, ge=1, le=3650),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db=Depends(get_db_connection),
    _: AuthenticatedUser = Depends(get_current_user),
):
    total = await db.fetchval(
        """
        SELECT COUNT(*)::int
        FROM signals
        WHERE entity_id=$1::uuid
          AND detected_at > NOW() - make_interval(days => $2)
          AND ($3::signal_type IS NULL OR signal_type = $3::signal_type)
        """,
        entity_id,
        days_back,
        signal_type,
    )
    rows = await db.fetch(
        """
        SELECT signal_type, description, confidence, impact_score, source_url, detected_at
        FROM signals
        WHERE entity_id=$1::uuid
          AND detected_at > NOW() - make_interval(days => $2)
          AND ($3::signal_type IS NULL OR signal_type = $3::signal_type)
        ORDER BY detected_at DESC, impact_score DESC
        LIMIT $4 OFFSET $5
        """,
        entity_id,
        days_back,
        signal_type,
        limit,
        offset,
    )
    return PaginatedResponse.build([dict(row) for row in rows], int(total or 0), limit, offset)
