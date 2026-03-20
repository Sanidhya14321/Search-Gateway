from collections.abc import AsyncGenerator

import asyncpg
from fastapi import Depends, Header, HTTPException

from backend.config import settings
from backend.database import get_pool


async def get_db_connection(pool: asyncpg.Pool = Depends(get_pool)) -> AsyncGenerator[asyncpg.Connection, None]:
    async with pool.acquire() as conn:
        yield conn


async def verify_api_key(x_api_key: str = Header(default="", alias="X-API-Key")) -> str:
    if x_api_key not in {settings.internal_service_api_key, settings.api_key}:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
