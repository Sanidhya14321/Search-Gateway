from types import SimpleNamespace

import pytest

from backend.agents.router import run_agent
from backend.crawler.queue_worker import process_crawl_item
from backend.services.retrieval.vector_search import ChunkResult, vector_search


@pytest.mark.asyncio
async def test_full_lead_finder(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            "INSERT INTO companies (canonical_id, canonical_name, domain) VALUES ('comp_int_example','Example Inc','example.com') RETURNING id"
        )

    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.lead_finder.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return SimpleNamespace(record={"id": company_id, "canonical_name": "Example Inc", "entity_type": "company"}, confidence=0.95, entity_type="company", canonical_name="Example Inc")

    async def _mock_llm(prompt: str, system: str = "", model=None):
        _ = system, model
        if "title_keywords" in prompt:
            return {"company_name": "Example Inc", "title_keywords": ["engineer"], "seniority": "senior"}
        return {
            "summary": "Example Inc appears to be hiring.",
            "facts": [{"claim": "Example is hiring engineers", "confidence": 0.9}],
            "people": [{"name": "Taylor", "title": "Senior Engineer", "confidence": 0.8}],
            "signals": [],
            "degraded": False,
        }

    async def _mock_vector(*args, **kwargs):
        _ = args, kwargs
        return [
            ChunkResult(
                id="int-chunk-1",
                chunk_text="Taylor is a Senior Engineer at Example Inc",
                source_doc_id="doc-1",
                entity_id=str(company_id),
                source_url="https://example.com/team",
                source_type="company_website",
                fetched_at=None,
                similarity=0.9,
                freshness_score=0.8,
                trust_score=0.8,
            )
        ]

    async def _mock_kw(*args, **kwargs):
        _ = args, kwargs
        return []

    monkeypatch.setattr("backend.agents.nodes.resolve_entity.resolve_entity", _mock_resolve)
    monkeypatch.setattr("backend.agents.nodes.parse_query.llm_json_call", _mock_llm)
    monkeypatch.setattr("backend.agents.nodes.synthesize.llm_json_call", _mock_llm)
    monkeypatch.setattr("backend.agents.nodes.vector_search_node.vector_search", _mock_vector)
    monkeypatch.setattr("backend.agents.nodes.rank_results.keyword_search", _mock_kw)

    result = await run_agent("lead_finder", "Find engineers at Example Inc")
    response = result.get("final_response", {})
    assert response.get("people")
    assert response.get("people")[0].get("citations")
    assert response.get("people")[0].get("citations")[0].get("url")
    assert response.get("summary")


@pytest.mark.asyncio
async def test_full_account_brief(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            "INSERT INTO companies (canonical_id, canonical_name, domain) VALUES ('comp_int_brief','Brief Inc','brief.com') RETURNING id"
        )
        await conn.execute(
            "INSERT INTO signals (entity_id, entity_type, signal_type, description, source_url) VALUES ($1::uuid, 'company', 'hiring', 'Hiring expansion', 'https://brief.com/news')",
            company_id,
        )

    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.account_brief.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return SimpleNamespace(record={"id": company_id, "canonical_name": "Brief Inc", "entity_type": "company"}, confidence=0.94, entity_type="company", canonical_name="Brief Inc")

    async def _mock_vector(*args, **kwargs):
        _ = args, kwargs
        return [
            ChunkResult(
                id="int-brief-chunk",
                chunk_text="Brief Inc has expanded hiring",
                source_doc_id="doc-b",
                entity_id=str(company_id),
                source_url="https://brief.com/hiring",
                source_type="news_article",
                fetched_at=None,
                similarity=0.85,
                freshness_score=0.8,
                trust_score=0.8,
            )
        ]

    async def _mock_kw(*args, **kwargs):
        _ = args, kwargs
        return []

    async def _mock_llm(*args, **kwargs):
        _ = args, kwargs
        return {"summary": "Brief summary", "facts": [], "people": [], "signals": [], "degraded": False}

    monkeypatch.setattr("backend.agents.nodes.resolve_entity.resolve_entity", _mock_resolve)
    monkeypatch.setattr("backend.agents.nodes.vector_search_node.vector_search", _mock_vector)
    monkeypatch.setattr("backend.agents.nodes.rank_results.keyword_search", _mock_kw)
    monkeypatch.setattr("backend.agents.nodes.synthesize.llm_json_call", _mock_llm)

    result = await run_agent("account_brief", "Account brief for Brief Inc")
    final_response = result.get("final_response", {})
    assert final_response.get("signal_timeline")
    assert final_response.get("summary")


@pytest.mark.asyncio
async def test_crawl_to_retrieval(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            "INSERT INTO companies (canonical_id, canonical_name, domain) VALUES ('comp_int_crawl','Crawl Inc','crawl.com') RETURNING id"
        )
        item = {
            "id": await conn.fetchval(
                "INSERT INTO crawl_queue (url, domain, entity_id, entity_type, priority) VALUES ('https://crawl.com', 'crawl.com', $1::uuid, 'company', 3) RETURNING id",
                company_id,
            ),
            "url": "https://crawl.com",
            "entity_id": company_id,
            "entity_type": "company",
            "attempts": 0,
            "max_attempts": 3,
        }

        async def _mock_fetch(url: str, **kwargs):
            _ = kwargs
            return {
                "url": url,
                "status": 200,
                "raw_html": "<html><body>Crawl Inc launched a new platform.</body></html>",
                "clean_text": "Crawl Inc launched a new platform.",
            }

        monkeypatch.setattr("backend.crawler.queue_worker.rate_limited_fetch", _mock_fetch)
        async def _mock_extract_signals(*args, **kwargs):
            _ = args, kwargs
            return []

        monkeypatch.setattr("backend.crawler.queue_worker.extract_signals", _mock_extract_signals)

        class _Embed:
            async def embed_batch(self, texts, batch_size=100):
                _ = batch_size
                return [[0.2] * 768 for _ in texts]

            async def embed(self, text):
                _ = text
                return [0.2] * 768

        await process_crawl_item(item, conn, _Embed())
        results = await vector_search("platform", entity_id=str(company_id), db=conn, embed_service=_Embed())

    assert results


@pytest.mark.asyncio
async def test_cache_hit(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            "INSERT INTO companies (canonical_id, canonical_name, domain) VALUES ('comp_int_cache','Cache Inc','cache.com') RETURNING id"
        )

    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.lead_finder.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return SimpleNamespace(record={"id": company_id, "canonical_name": "Cache Inc", "entity_type": "company"}, confidence=0.95, entity_type="company", canonical_name="Cache Inc")

    async def _mock_llm(prompt: str, system: str = "", model=None):
        _ = prompt, system, model
        return {"summary": "Cache response", "facts": [], "people": [], "signals": [], "degraded": False}

    async def _mock_vector(*args, **kwargs):
        _ = args, kwargs
        return []

    async def _mock_kw(*args, **kwargs):
        _ = args, kwargs
        return []

    monkeypatch.setattr("backend.agents.nodes.resolve_entity.resolve_entity", _mock_resolve)
    async def _mock_parse_llm(*args, **kwargs):
        _ = args, kwargs
        return {"company_name": "Cache Inc", "title_keywords": [], "seniority": "unknown"}

    monkeypatch.setattr("backend.agents.nodes.parse_query.llm_json_call", _mock_parse_llm)
    monkeypatch.setattr("backend.agents.nodes.synthesize.llm_json_call", _mock_llm)
    monkeypatch.setattr("backend.agents.nodes.vector_search_node.vector_search", _mock_vector)
    monkeypatch.setattr("backend.agents.nodes.rank_results.keyword_search", _mock_kw)

    first = await run_agent("lead_finder", "Find people at Cache Inc")
    second = await run_agent("lead_finder", "Find people at Cache Inc")

    assert first.get("cache_hit") is not True
    assert second.get("cache_hit") is True


@pytest.mark.asyncio
async def test_batch_enrichment(client_authed, db_pool, monkeypatch):
    monkeypatch.setattr("backend.routers.enrich.get_pool", lambda: db_pool)

    async def _fake_run_agent(workflow_name: str, query: str, **kwargs):
        _ = workflow_name, query, kwargs
        return {
            "final_response": {
                "enriched_rows": [
                    {"canonical_id": "pers_one", "citations": [{"url": "https://example.com/one"}]},
                    {"canonical_id": "pers_two", "citations": [{"url": "https://example.com/two"}]},
                    {"canonical_id": "pers_three", "citations": [{"url": "https://example.com/three"}]},
                    {"canonical_id": "pers_four", "citations": [{"url": "https://example.com/four"}]},
                    {"canonical_id": "pers_five", "citations": [{"url": "https://example.com/five"}]},
                ]
            }
        }

    monkeypatch.setattr("backend.routers.enrich.run_agent", _fake_run_agent)

    payload = {"leads": [{"name": f"Lead {idx}", "company": "Example"} for idx in range(5)]}
    queued = await client_authed.post("/api/v1/enrich/batch", json=payload)
    assert queued.status_code == 200

    job_id = queued.json()["job_id"]
    completed = None
    for _ in range(20):
        response = await client_authed.get(f"/api/v1/enrich/batch/{job_id}")
        body = response.json()
        if body.get("status") == "completed":
            completed = body
            break

    assert completed is not None
    rows = completed["result"].get("enriched_rows", [])
    assert len(rows) == 5
    assert all(row.get("canonical_id") for row in rows)
    assert all((row.get("citations") or [{}])[0].get("url") for row in rows)
