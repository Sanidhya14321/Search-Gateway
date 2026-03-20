from datetime import datetime, timedelta, timezone

import pytest

from backend.crawler.chunker import chunk_text
from backend.crawler.extractor import extract_clean_text
from backend.crawler.queue_worker import process_crawl_item_by_id
from backend.crawler.store import compute_content_hash
from backend.dependencies import get_db_connection
from backend.main import app
from backend.scoring.freshness import compute_freshness_score
from backend.services.retrieval.keyword_search import keyword_search
from backend.services.retrieval.merger import merge_results_rrf
from backend.services.retrieval.ranker import rank_chunks
from backend.services.retrieval.vector_search import ChunkResult, vector_search


class FakeEmbeddingService:
    def __init__(self, vector):
        self._vector = vector

    async def embed(self, text: str) -> list[float]:
        _ = text
        return self._vector


@pytest.mark.asyncio
async def test_extract_clean_text():
    html = """
    <html>
      <head><script>ignore()</script><style>.x{}</style></head>
      <body>
        <nav>menu</nav>
        <main><h1>Acme</h1><p>Hiring now</p></main>
      </body>
    </html>
    """
    cleaned = extract_clean_text(html)

    assert "Acme" in cleaned
    assert "Hiring now" in cleaned
    assert "menu" not in cleaned
    assert "ignore" not in cleaned


@pytest.mark.asyncio
async def test_chunk_text():
    text = "A" * 1200 + "B" * 1200
    chunks = chunk_text(text, chunk_size=512, chunk_overlap=64)

    assert len(chunks) >= 4
    assert all(len(chunk) <= 512 for chunk in chunks)
    assert chunks[0][-64:] == chunks[1][:64]


@pytest.mark.asyncio
async def test_content_hash_consistency():
    text = "same text"
    assert compute_content_hash(text) == compute_content_hash(text)
    assert compute_content_hash(text) != compute_content_hash("different text")


@pytest.mark.asyncio
async def test_vector_search(db_pool):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            """
            INSERT INTO companies (canonical_id, canonical_name)
            VALUES ('comp_v_test', 'Vector Co')
            RETURNING id
            """
        )
        source_doc_id = await conn.fetchval(
            """
            INSERT INTO source_documents (source_url, source_type, entity_id, entity_type, clean_text, content_hash)
            VALUES ('https://example.com/v', 'company_website', $1::uuid, 'company', 'vector doc', 'h1')
            RETURNING id
            """,
            company_id,
        )

        vector_a = [1.0] + [0.0] * 767
        vector_b = [0.0, 1.0] + [0.0] * 766

        await conn.execute(
            """
            INSERT INTO chunks (source_doc_id, chunk_index, chunk_text, entity_id, entity_type, embedding, embed_model_id)
            VALUES ($1::uuid, 0, 'alpha funding', $2::uuid, 'company', $3::vector, 'nomic-embed-text')
            """,
            source_doc_id,
            company_id,
            vector_a,
        )
        await conn.execute(
            """
            INSERT INTO chunks (source_doc_id, chunk_index, chunk_text, entity_id, entity_type, embedding, embed_model_id)
            VALUES ($1::uuid, 1, 'beta hiring', $2::uuid, 'company', $3::vector, 'nomic-embed-text')
            """,
            source_doc_id,
            company_id,
            vector_b,
        )

        fake_embed = FakeEmbeddingService(vector_a)
        results = await vector_search("funding", entity_id=str(company_id), top_k=3, db=conn, embed_service=fake_embed)

    assert results
    assert results[0].chunk_text == "alpha funding"


@pytest.mark.asyncio
async def test_keyword_search(db_pool):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            """
            INSERT INTO companies (canonical_id, canonical_name)
            VALUES ('comp_k_test', 'Keyword Co')
            RETURNING id
            """
        )
        source_doc_id = await conn.fetchval(
            """
            INSERT INTO source_documents (source_url, source_type, entity_id, entity_type, clean_text, content_hash)
            VALUES ('https://example.com/k', 'company_website', $1::uuid, 'company', 'keyword doc', 'h2')
            RETURNING id
            """,
            company_id,
        )
        await conn.execute(
            """
            INSERT INTO chunks (source_doc_id, chunk_index, chunk_text, entity_id, entity_type, embedding, embed_model_id)
            VALUES ($1::uuid, 0, 'acme announced funding round', $2::uuid, 'company', $3::vector, 'nomic-embed-text')
            """,
            source_doc_id,
            company_id,
            [1.0] + [0.0] * 767,
        )

        results = await keyword_search("funding", entity_id=str(company_id), top_k=3, db=conn)

    assert results
    assert "funding" in results[0].chunk_text


@pytest.mark.asyncio
async def test_merge_rrf():
    fetched = datetime.now(timezone.utc)
    a = ChunkResult(
        id="a",
        chunk_text="a",
        source_doc_id="s1",
        entity_id=None,
        source_url="https://example.com/a",
        source_type="company_website",
        fetched_at=fetched,
        similarity=0.9,
    )
    b = ChunkResult(
        id="b",
        chunk_text="b",
        source_doc_id="s1",
        entity_id=None,
        source_url="https://example.com/b",
        source_type="company_website",
        fetched_at=fetched,
        similarity=0.8,
    )
    c = ChunkResult(
        id="c",
        chunk_text="c",
        source_doc_id="s1",
        entity_id=None,
        source_url="https://example.com/c",
        source_type="company_website",
        fetched_at=fetched,
        similarity=0.7,
    )

    merged = merge_results_rrf([a, b], [b, c])
    assert [item.id for item in merged][:2] == ["b", "a"]


@pytest.mark.asyncio
async def test_rank_chunks():
    now = datetime.now(timezone.utc)
    strong = ChunkResult(
        id="strong",
        chunk_text="strong",
        source_doc_id="s1",
        entity_id=None,
        source_url="https://crunchbase.com/company/acme",
        source_type="crunchbase",
        fetched_at=now,
        similarity=0.7,
        freshness_score=0.9,
        trust_score=0.9,
    )
    weak = ChunkResult(
        id="weak",
        chunk_text="weak",
        source_doc_id="s2",
        entity_id=None,
        source_url="https://unknown.example/post",
        source_type="unknown",
        fetched_at=now - timedelta(days=40),
        similarity=0.72,
        freshness_score=0.2,
        trust_score=0.3,
    )

    ranked = rank_chunks([weak, strong])
    assert ranked[0].id == "strong"


@pytest.mark.asyncio
async def test_compute_freshness_today():
    score = compute_freshness_score(datetime.now(timezone.utc))
    assert score >= 0.99


@pytest.mark.asyncio
async def test_compute_freshness_30_days():
    score = compute_freshness_score(datetime.now(timezone.utc) - timedelta(days=30))
    assert score < 0.5


@pytest.mark.asyncio
async def test_crawl_endpoint_robots_blocked(client, db_pool, monkeypatch):
    async def _override_db():
        async with db_pool.acquire() as conn:
            yield conn

    monkeypatch.setattr("backend.routers.crawl.is_allowed", lambda _: False)
    app.dependency_overrides[get_db_connection] = _override_db

    try:
        response = await client.post("/api/v1/crawl", json={"url": "https://example.com"})
    finally:
        app.dependency_overrides.pop(get_db_connection, None)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_process_crawl_item_by_id_persists_chunks(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            """
            INSERT INTO companies (canonical_id, canonical_name)
            VALUES ('comp_queue_test', 'Queue Co')
            RETURNING id
            """
        )
        crawl_id = await conn.fetchval(
            """
            INSERT INTO crawl_queue (url, domain, entity_id, entity_type, priority, max_attempts)
            VALUES ('https://example.com/queue', 'example.com', $1::uuid, 'company', 5, 3)
            RETURNING id
            """,
            company_id,
        )

        async def _fake_fetch(url: str, **kwargs):
            _ = kwargs
            return {
                "url": url,
                "status": 200,
                "raw_html": "<html><body><h1>Example Company</h1><p>Funding update announced.</p></body></html>",
                "clean_text": "Example Company Funding update announced.",
            }

        monkeypatch.setattr("backend.crawler.queue_worker.rate_limited_fetch", _fake_fetch)

        async def _fake_signals(*args, **kwargs):
            _ = args, kwargs
            return []

        monkeypatch.setattr("backend.crawler.queue_worker.extract_signals", _fake_signals)

        class _Embed:
            async def embed_batch(self, texts, batch_size=100):
                _ = batch_size
                return [[0.1] * 768 for _ in texts]

        await process_crawl_item_by_id(conn, _Embed(), str(crawl_id))

        chunk_count = await conn.fetchval(
            """
            SELECT COUNT(*)::int
            FROM chunks c
            JOIN source_documents sd ON sd.id = c.source_doc_id
            WHERE sd.source_url = 'https://example.com/queue'
            """
        )
        status = await conn.fetchval("SELECT status FROM crawl_queue WHERE id=$1::uuid", crawl_id)

    assert chunk_count > 0
    assert status == "completed"
