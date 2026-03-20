from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.dependencies import get_db_connection

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(db=Depends(get_db_connection)):
    try:
        await db.fetchval("SELECT 1")
        return {
            "status": "ok",
            "db": "connected",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "db": "unreachable",
                "error": str(exc),
                "version": "1.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
