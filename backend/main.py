import os
import re
import subprocess
import sys
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


def run_migrations() -> None:
    direct_url = settings.database_url_direct or settings.database_url
    normalized_url = (
        direct_url.replace("postgres://", "postgresql://", 1)
        if direct_url.startswith("postgres://")
        else direct_url
    )

    env = os.environ.copy()
    # Alembic env.py reads DATABASE_URL_DIRECT / DATABASE_URL. Keep both in sync for startup migration runs.
    env["DATABASE_URL_DIRECT"] = normalized_url
    env["DATABASE_URL"] = normalized_url

    logger.info("migrations_start | target=head")

    def run_upgrade() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    proc = run_upgrade()
    if proc.returncode != 0 and "relation \"chunks\" does not exist" in (proc.stderr or ""):
        logger.warning("migrations_bootstrap_needed | reason=missing_chunks")
        bootstrap = subprocess.run(
            [sys.executable, "scripts/init_db.py"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if bootstrap.returncode != 0:
            logger.error("bootstrap_failed | code={} stderr={}", bootstrap.returncode, bootstrap.stderr.strip())
            raise RuntimeError("Startup schema bootstrap failed")
        proc = run_upgrade()

    if proc.returncode != 0:
        logger.error("migrations_failed | code={} stderr={}", proc.returncode, proc.stderr.strip())
        raise RuntimeError("Startup migrations failed")
    logger.info("migrations_done | target=head")


@asynccontextmanager
async def lifespan(_: FastAPI):
    run_migrations()
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
cors_origins = [origin.rstrip("/") for origin in settings.cors_allowed_origins_list] or ["http://localhost:3000"]
cors_origin_regex = settings.cors_allow_origin_regex or ""
try:
    compiled_cors_origin_regex = re.compile(cors_origin_regex) if cors_origin_regex else None
except re.error:
    compiled_cors_origin_regex = None
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex or None,
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [search, enrich, entities, accounts, contacts, crawl, signals, agents, health, auth, user]:
    app.include_router(router.router, prefix="/api/v1")


def _origin_is_allowed(origin: str) -> bool:
    normalized_origin = origin.rstrip("/")
    if "*" in cors_origins or normalized_origin in cors_origins:
        return True
    if compiled_cors_origin_regex and compiled_cors_origin_regex.fullmatch(normalized_origin):
        return True
    return False


@app.middleware("http")
async def ensure_cors_headers_middleware(request, call_next):
    response = await call_next(request)
    origin = request.headers.get("origin")
    if not origin or not _origin_is_allowed(origin):
        return response

    response.headers.setdefault("Access-Control-Allow-Origin", origin.rstrip("/"))
    response.headers.setdefault("Vary", "Origin")
    if "*" not in cors_origins:
        response.headers.setdefault("Access-Control-Allow-Credentials", "true")

    if request.method.upper() == "OPTIONS":
        response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        requested_headers = request.headers.get("access-control-request-headers")
        response.headers.setdefault(
            "Access-Control-Allow-Headers",
            requested_headers or "Authorization,Content-Type,X-Trace-ID",
        )

    return response


def _error_cors_headers(request) -> dict[str, str]:
    origin = request.headers.get("origin")
    if not origin:
        return {}
    if _origin_is_allowed(origin):
        return {
            "Access-Control-Allow-Origin": origin.rstrip("/"),
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
    return {}


@app.exception_handler(CRMindError)
async def handle_crmind_error(request, exc: CRMindError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": str(exc),
            "path": str(request.url.path),
        },
        headers=_error_cors_headers(request),
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
        headers=_error_cors_headers(request),
    )
