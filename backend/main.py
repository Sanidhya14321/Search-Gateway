from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config import settings
from backend.database import close_pool, create_pool
from backend.middleware.trace import trace_timing_middleware
from backend.routers import accounts, agents, auth, contacts, crawl, enrich, entities, health, search, signals, user
from backend.utils.exceptions import CRMindError


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_pool()
    try:
        yield
    finally:
        await close_pool()


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=settings.log_level,
        serialize=settings.log_format.lower() == "json",
    )


configure_logging()

app = FastAPI(title="CRMind API", version="1.0.0", lifespan=lifespan)
app.middleware("http")(trace_timing_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [search, enrich, entities, accounts, contacts, crawl, signals, agents, health, auth, user]:
    app.include_router(router.router, prefix="/api/v1")


@app.exception_handler(CRMindError)
async def handle_crmind_error(request, exc: CRMindError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": str(exc),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request, exc: Exception):
    logger.exception(f"unhandled_error | path={request.url.path} error={type(exc).__name__}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
        },
    )
