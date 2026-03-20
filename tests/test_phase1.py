from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from backend.dependencies import get_db_connection
from backend.main import app
from backend.services import entity_resolver


class _FakeAcquire:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakePool:
    def __init__(self, conn):
        self._conn = conn

    def acquire(self):
        return _FakeAcquire(self._conn)


class _FakeResolverConn:
    def __init__(self):
        self._domain_row = {
            "id": "c1",
            "canonical_id": "comp_example_inc",
            "canonical_name": "Example Inc",
            "domain": "example.com",
            "aliases": ["example inc", "example"],
        }

    async def fetchrow(self, query: str, value):
        if "WHERE domain = $1" in query and value == "example.com":
            return self._domain_row
        if "ANY(aliases)" in query and value in {"example inc", "example"}:
            return self._domain_row
        return None

    async def fetch(self, query: str, value):
        if "similarity(canonical_name, $1)" in query and value in {"exampl", "exampl corp", "example"}:
            return [
                {
                    "id": "c1",
                    "canonical_id": "comp_example_inc",
                    "canonical_name": "Example Inc",
                    "domain": "example.com",
                    "aliases": ["example inc"],
                    "sim": 0.65,
                }
            ]
        return []


class _HealthyConn:
    async def fetchval(self, query: str):
        _ = query
        return 1


@pytest.mark.asyncio
async def test_health_ok() -> None:
    async def override_db() -> AsyncIterator[_HealthyConn]:
        yield _HealthyConn()

    app.dependency_overrides[get_db_connection] = override_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.get("/api/v1/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["db"] == "connected"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_db_down() -> None:
    class _BrokenConn:
        async def fetchval(self, query: str):
            _ = query
            raise RuntimeError("db down")

    async def override_db() -> AsyncIterator[None]:
        yield _BrokenConn()

    app.dependency_overrides[get_db_connection] = override_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/api/v1/health")
        assert response.status_code == 503
        payload = response.json()
        assert payload["status"] == "degraded"
        assert payload["db"] == "unreachable"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_entity_resolver_exact_domain(monkeypatch) -> None:
    fake_conn = _FakeResolverConn()

    async def fake_get_pool():
        return _FakePool(fake_conn)

    monkeypatch.setattr(entity_resolver, "get_pool", fake_get_pool)

    result = await entity_resolver.resolve_entity("example.com")
    assert result is not None
    assert result.confidence >= 0.95
    assert result.canonical_id == "comp_example_inc"


@pytest.mark.asyncio
async def test_entity_resolver_fuzzy(monkeypatch) -> None:
    fake_conn = _FakeResolverConn()

    async def fake_get_pool():
        return _FakePool(fake_conn)

    monkeypatch.setattr(entity_resolver, "get_pool", fake_get_pool)

    result = await entity_resolver.resolve_entity("Exampl Corp")
    assert result is not None
    assert result.confidence >= 0.6
    assert result.canonical_id == "comp_example_inc"


@pytest.mark.asyncio
async def test_entity_resolver_not_found(monkeypatch) -> None:
    class _NotFoundConn(_FakeResolverConn):
        async def fetchrow(self, query: str, value):
            _ = query, value
            return None

        async def fetch(self, query: str, value):
            _ = query, value
            return []

    async def fake_get_pool():
        return _FakePool(_NotFoundConn())

    monkeypatch.setattr(entity_resolver, "get_pool", fake_get_pool)

    result = await entity_resolver.resolve_entity("zzzunknown999xyz")
    assert result is None


def test_normalize_domain() -> None:
    assert entity_resolver.normalize_domain("https://www.Acme.com/") == "acme.com"
