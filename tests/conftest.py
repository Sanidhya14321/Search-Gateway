import asyncio
import hashlib
import os
import sys
import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import numpy as np
import pgvector.asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings
from backend.database import close_pool, create_pool
from backend.database import get_pool as get_runtime_pool
from backend.middleware.auth import AuthenticatedUser, get_current_user
from backend.main import app


@pytest.fixture(scope="function")
async def db_pool() -> AsyncIterator[asyncpg.Pool]:
    test_dsn = os.getenv("TEST_DATABASE_URL", settings.database_url.replace("/crmind", "/crmind_test"))
    async def _init_connection(conn: asyncpg.Connection) -> None:
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
        await pgvector.asyncpg.register_vector(conn)

    pool = await asyncpg.create_pool(dsn=test_dsn, min_size=1, max_size=5, init=_init_connection)
    yield pool
    await pool.close()


@pytest.fixture(autouse=True)
async def clean_tables(db_pool: asyncpg.Pool) -> AsyncIterator[None]:
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            DO $$
            DECLARE r RECORD;
            BEGIN
                FOR r IN (
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                ) LOOP
                    EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' RESTART IDENTITY CASCADE';
                END LOOP;
            END $$;
            """
        )
    yield


@pytest.fixture
async def seeded_company(db_pool: asyncpg.Pool) -> dict:
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            """
            INSERT INTO companies (canonical_id, canonical_name, domain, trust_score, freshness_score)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            "comp_test_inc",
            "Test Inc",
            "test.com",
            0.5,
            0.5,
        )
    return {"id": company_id, "canonical_id": "comp_test_inc", "canonical_name": "Test Inc"}


@pytest.fixture
async def seeded_person(db_pool: asyncpg.Pool, seeded_company: dict) -> dict:
    async with db_pool.acquire() as conn:
        person_id = await conn.fetchval(
            """
            INSERT INTO people (canonical_id, full_name, seniority_level, current_company_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            "pers_jane_doe",
            "Jane Doe",
            "senior",
            seeded_company["id"],
        )
    return {"id": person_id, "canonical_id": "pers_jane_doe", "full_name": "Jane Doe"}


@pytest.fixture
async def seeded_source_and_chunks(db_pool: asyncpg.Pool, seeded_company: dict) -> dict:
    async with db_pool.acquire() as conn:
        source_doc_id = await conn.fetchval(
            """
            INSERT INTO source_documents (entity_id, entity_type, source_url, source_type, clean_text, content_hash)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            seeded_company["id"],
            "company",
            "https://example.test/doc",
            "company_website",
            "Alpha beta gamma",
            hashlib.sha256("Alpha beta gamma".encode("utf-8")).hexdigest(),
        )

        chunk_texts = ["alpha insights", "beta updates", "gamma roadmap"]
        chunk_ids = []
        for idx, text in enumerate(chunk_texts):
            seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
            rng = np.random.default_rng(seed)
            vector = rng.random(768).astype(np.float32).tolist()
            chunk_id = await conn.fetchval(
                """
                INSERT INTO chunks (
                    source_doc_id, entity_id, entity_type, chunk_text, chunk_index,
                    embedding, embed_model_id, freshness_score, trust_score
                )
                VALUES ($1, $2, $3, $4, $5, $6::vector, $7, $8, $9)
                RETURNING id
                """,
                source_doc_id,
                seeded_company["id"],
                "company",
                text,
                idx,
                vector,
                settings.embedding_model,
                0.5,
                0.5,
            )
            chunk_ids.append(chunk_id)

    return {"source_doc_id": source_doc_id, "chunk_ids": chunk_ids}


@pytest.fixture
def mock_llm(monkeypatch):
    mock = AsyncMock(return_value={"summary": "mocked", "facts": [], "people": [], "citations": []})
    monkeypatch.setattr("backend.agents.llm_client.llm_json_call_with_fallback", mock)
    return mock


@pytest.fixture
def mock_embed(monkeypatch):
    async def _embed(self, text: str) -> list[float]:
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)
        rng = np.random.default_rng(seed)
        return rng.random(768).astype(np.float32).tolist()

    monkeypatch.setattr("backend.services.embedding_service.EmbeddingService.embed", _embed)
    return _embed


@pytest.fixture
def mock_crawler(monkeypatch):
    async def _fetch_page(url: str, **kwargs) -> dict:
        _ = kwargs
        return {"url": url, "status": 200, "raw_html": "<html><body>ok</body></html>", "clean_text": "ok"}

    async def _rate_limited_fetch(url: str, **kwargs) -> dict:
        return await _fetch_page(url, **kwargs)

    monkeypatch.setattr("backend.crawler.fetcher.fetch_page", _fetch_page)
    monkeypatch.setattr("backend.crawler.rate_limiter.rate_limited_fetch", _rate_limited_fetch)
    return {"fetch_page": _fetch_page, "rate_limited_fetch": _rate_limited_fetch}


@pytest.fixture
async def client(db_pool: asyncpg.Pool) -> AsyncIterator[AsyncClient]:
    async def _override_pool() -> asyncpg.Pool:
        return db_pool

    app.dependency_overrides[create_pool] = _override_pool
    app.dependency_overrides[get_runtime_pool] = _override_pool
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    await close_pool()


@pytest_asyncio.fixture
async def seeded_user(db_pool: asyncpg.Pool) -> dict:
    supabase_id = uuid.uuid4()
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (supabase_user_id, email, display_name, plan)
            VALUES ($1, 'test@example.com', 'Test User', 'free')
            RETURNING *
            """,
            supabase_id,
        )
    return dict(row)


@pytest.fixture
def mock_auth(seeded_user: dict):
    test_user = AuthenticatedUser(
        user_id=str(seeded_user["id"]),
        supabase_user_id=str(seeded_user["supabase_user_id"]),
        email="test@example.com",
        plan="free",
        auth_method="jwt",
    )

    async def _override_current_user() -> AuthenticatedUser:
        return test_user

    app.dependency_overrides[get_current_user] = _override_current_user
    return test_user


@pytest_asyncio.fixture
async def client_authed(db_pool: asyncpg.Pool, mock_auth: AuthenticatedUser) -> AsyncIterator[AsyncClient]:
    async def _override_pool() -> asyncpg.Pool:
        return db_pool

    app.dependency_overrides[create_pool] = _override_pool
    app.dependency_overrides[get_runtime_pool] = _override_pool
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        test_client.headers["Authorization"] = "Bearer fake-test-token"
        yield test_client

    app.dependency_overrides.clear()
    await close_pool()
