---
name: fastapi-backend-structure
description: >
  Define and implement the FastAPI backend structure for CRMind. Use this skill when
  creating API routes, request/response models, middleware, database connections,
  dependency injection, error handling, or background task setup. Keywords: FastAPI,
  API routes, Pydantic, endpoint, async, database, dependency injection, middleware,
  background tasks, CORS, authentication, rate limiting.
---

## Project Structure

```
backend/
├── main.py                    ← FastAPI app + router registration
├── config.py                  ← Settings via pydantic-settings
├── database.py                ← Async Postgres pool (asyncpg)
├── dependencies.py            ← Shared FastAPI deps (db, auth)
│
├── routers/
│   ├── search.py              ← POST /api/v1/search
│   ├── enrich.py              ← POST /api/v1/enrich (single + batch)
│   ├── entities.py            ← GET /api/v1/entity/{id}
│   ├── accounts.py            ← GET /api/v1/account/{id}/brief
│   ├── contacts.py            ← GET /api/v1/contact/{id}
│   ├── crawl.py               ← POST /api/v1/crawl
│   ├── signals.py             ← GET /api/v1/signals/{entity_id}
│   ├── agents.py              ← POST /api/v1/agent/run
│   └── health.py              ← GET /api/v1/health
│
├── models/
│   ├── requests.py            ← Pydantic request schemas
│   ├── responses.py           ← Pydantic response schemas
│   └── db_models.py           ← Internal DB row models
│
├── services/
│   ├── entity_resolver.py
│   ├── retrieval/
│   ├── scoring/
│   └── agents/
│
├── crawler/
└── tests/
```

---

## main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_pool, close_pool
from routers import search, enrich, entities, accounts, contacts, crawl, signals, agents, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    yield
    await close_pool()

app = FastAPI(
    title="CRMind API",
    version="1.0.0",
    description="Entity-first, citation-aware CRM intelligence API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
for router in [search, enrich, entities, accounts, contacts, crawl, signals, agents, health]:
    app.include_router(router.router, prefix="/api/v1")
```

---

## config.py

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379"
    groq_api_key: str = ""
    groq_llm_model: str = "llama-3.3-70b-versatile"
    groq_llm_model_fallback: str = "llama-3.1-8b-instant"
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    top_k_retrieval: int = 20
    top_k_final: int = 8
    min_similarity: float = 0.3
    crawl_min_delay_seconds: float = 3.0
    respect_robots_txt: bool = True
    cache_ttl_seconds: int = 3600
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## database.py

```python
import asyncpg
from config import settings

_pool: asyncpg.Pool | None = None

async def create_pool():
    global _pool
    _pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )

async def close_pool():
    if _pool:
        await _pool.close()

async def get_pool() -> asyncpg.Pool:
    return _pool
```

---

## dependencies.py

```python
from fastapi import Depends, HTTPException, Header
from database import get_pool
from config import settings

async def get_db(pool=Depends(get_pool)):
    async with pool.acquire() as conn:
        yield conn

async def verify_api_key(x_api_key: str = Header(...)):
    # Simple API key check — replace with JWT for production
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

---

## Canonical Response Models (models/responses.py)

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SourceCitation(BaseModel):
    source_id: str
    url: str
    source_type: str
    fetched_at: datetime
    excerpt: Optional[str] = None
    trust_score: float
    freshness_score: float

class PersonResult(BaseModel):
    canonical_id: str
    full_name: str
    current_title: Optional[str]
    seniority_level: str
    company_name: Optional[str]
    linkedin_url: Optional[str]
    confidence: float
    sources: List[SourceCitation]

class SignalResult(BaseModel):
    signal_type: str
    description: str
    confidence: float
    impact_score: float
    source_url: Optional[str]
    detected_at: datetime

class EntityResponse(BaseModel):
    entity_id: str
    entity_type: str
    canonical_name: str
    confidence: float
    summary: Optional[str]
    facts: List[dict]
    signals: List[SignalResult]
    people: List[PersonResult]
    citations: List[SourceCitation]
    retrieved_at: datetime
    pipeline_version: str = "1.0.0"

class AgentRunResponse(BaseModel):
    run_id: str
    workflow_name: str
    status: str
    result: Optional[dict]
    steps_log: List[str]
    duration_ms: int
    citations: List[SourceCitation]
```

---

## Example Router (routers/agents.py)

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from models.requests import AgentRunRequest
from models.responses import AgentRunResponse
from services.agents.router import run_agent
from dependencies import get_db, verify_api_key
from database import get_pool
import time, uuid

router = APIRouter(prefix="/agent", tags=["agents"])

@router.post("/run", response_model=AgentRunResponse)
async def run_agent_endpoint(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    _=Depends(verify_api_key),
):
    run_id = str(uuid.uuid4())
    start = time.time()

    # Log run start
    await db.execute("""
        INSERT INTO agent_runs (run_id, workflow_name, status, input_payload)
        VALUES ($1, $2, 'running', $3)
    """, run_id, request.workflow_name, request.dict())

    try:
        result = await run_agent(
            workflow_name=request.workflow_name,
            query=request.query,
            entity_id=request.entity_id,
        )
        duration_ms = int((time.time() - start) * 1000)

        await db.execute("""
            UPDATE agent_runs
            SET status='completed', output_payload=$1, duration_ms=$2, completed_at=NOW()
            WHERE run_id=$3
        """, result, duration_ms, run_id)

        return AgentRunResponse(
            run_id=run_id,
            workflow_name=request.workflow_name,
            status="completed",
            result=result.get("final_response"),
            steps_log=result.get("steps_log", []),
            duration_ms=duration_ms,
            citations=result.get("citations", []),
        )
    except Exception as e:
        await db.execute("""
            UPDATE agent_runs SET status='failed', error_message=$1 WHERE run_id=$2
        """, str(e), run_id)
        raise
```

---

## Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": type(exc).__name__,
            "detail": str(exc),
            "path": request.url.path,
        },
    )
```

---

## Environment Variables Required

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/crmind
REDIS_URL=redis://localhost:6379
OLLAMA_BASE_URL=http://localhost:11434
API_KEY=your-secret-key
LOG_LEVEL=INFO
```