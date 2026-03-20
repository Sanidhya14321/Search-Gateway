from types import SimpleNamespace

import pytest

from backend.agents.router import classify_intent, run_agent
from backend.services.citations.validator import validate_citations
from backend.services.retrieval.vector_search import ChunkResult


@pytest.mark.asyncio
async def test_lead_finder_happy_path(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            """
            INSERT INTO companies (canonical_id, canonical_name)
            VALUES ('comp_phase3_lead', 'Acme Inc')
            RETURNING id
            """
        )
        await conn.execute(
            """
            INSERT INTO people (canonical_id, full_name, current_title, seniority_level, current_company_id)
            VALUES ('pers_jane_phase3', 'Jane Doe', 'Senior Engineer', 'senior', $1::uuid)
            """,
            company_id,
        )

    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.lead_finder.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return SimpleNamespace(
            record={"id": company_id, "canonical_name": "Acme Inc", "entity_type": "company"},
            confidence=0.95,
            entity_type="company",
            canonical_name="Acme Inc",
        )

    async def _mock_llm(prompt: str, system: str = "", model=None):
        _ = system, model
        if "title_keywords" in prompt:
            return {"company_name": "Acme Inc", "title_keywords": ["engineer"], "seniority": "senior"}
        return {
            "summary": "Grounded response",
            "facts": [{"claim": "Acme is hiring engineers", "confidence": 0.88}],
            "people": [{"name": "Jane Doe", "title": "Senior Engineer", "confidence": 0.9}],
            "signals": [],
            "degraded": False,
        }

    async def _mock_vector_search(*args, **kwargs):
        _ = args, kwargs
        return [
            ChunkResult(
                id="chunk-1",
                chunk_text="Jane Doe is a Senior Engineer at Acme.",
                source_doc_id="doc-1",
                entity_id=str(company_id),
                source_url="https://example.com/acme-team",
                source_type="company_website",
                fetched_at=None,
                similarity=0.92,
                freshness_score=0.8,
                trust_score=0.85,
            )
        ]

    async def _mock_keyword_search(*args, **kwargs):
        _ = args, kwargs
        return []

    monkeypatch.setattr("backend.agents.nodes.resolve_entity.resolve_entity", _mock_resolve)
    monkeypatch.setattr("backend.agents.nodes.parse_query.llm_json_call", _mock_llm)
    monkeypatch.setattr("backend.agents.nodes.synthesize.llm_json_call", _mock_llm)
    monkeypatch.setattr("backend.agents.nodes.vector_search_node.vector_search", _mock_vector_search)
    monkeypatch.setattr("backend.agents.nodes.rank_results.keyword_search", _mock_keyword_search)

    result = await run_agent("lead_finder", "Find senior engineers at Acme")
    people = result.get("final_response", {}).get("people", [])

    assert people
    assert people[0]["citations"]
    assert people[0]["citations"][0]["url"]


@pytest.mark.asyncio
async def test_lead_finder_entity_not_found(db_pool, monkeypatch):
    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.lead_finder.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return None

    async def _mock_llm(prompt: str, system: str = "", model=None):
        _ = prompt, system, model
        return {"company_name": "Unknown", "title_keywords": [], "seniority": "unknown"}

    monkeypatch.setattr("backend.agents.nodes.resolve_entity.resolve_entity", _mock_resolve)
    monkeypatch.setattr("backend.agents.nodes.parse_query.llm_json_call", _mock_llm)

    result = await run_agent("lead_finder", "Find engineers at Unknown")

    assert result.get("error") is not None
    assert result.get("final_response", {}).get("people") == []


@pytest.mark.asyncio
async def test_account_brief_has_signals(db_pool, monkeypatch):
    async with db_pool.acquire() as conn:
        company_id = await conn.fetchval(
            """
            INSERT INTO companies (canonical_id, canonical_name)
            VALUES ('comp_phase3_brief', 'Acme Brief Inc')
            RETURNING id
            """
        )
        await conn.execute(
            """
            INSERT INTO signals (entity_id, entity_type, signal_type, description, source_url)
            VALUES ($1::uuid, 'company', 'hiring', 'Opened 10 roles', 'https://example.com/jobs')
            """,
            company_id,
        )
        await conn.execute(
            """
            INSERT INTO signals (entity_id, entity_type, signal_type, description, source_url)
            VALUES ($1::uuid, 'company', 'funding', 'Raised Series A', 'https://example.com/funding')
            """,
            company_id,
        )

    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.account_brief.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return SimpleNamespace(
            record={"id": company_id, "canonical_name": "Acme Brief Inc", "entity_type": "company"},
            confidence=0.95,
            entity_type="company",
            canonical_name="Acme Brief Inc",
        )

    async def _mock_vector_search(*args, **kwargs):
        _ = args, kwargs
        return [
            ChunkResult(
                id="chunk-brief",
                chunk_text="Acme Brief Inc has hiring momentum.",
                source_doc_id="doc-brief",
                entity_id=str(company_id),
                source_url="https://example.com/brief",
                source_type="news_article",
                fetched_at=None,
                similarity=0.8,
                freshness_score=0.8,
                trust_score=0.8,
            )
        ]

    async def _mock_keyword_search(*args, **kwargs):
        _ = args, kwargs
        return []

    async def _mock_llm(prompt: str, system: str = "", model=None):
        _ = prompt, system, model
        return {
            "summary": "Account brief summary",
            "facts": [{"claim": "The account has active hiring", "confidence": 0.8}],
            "people": [],
            "signals": [],
            "degraded": False,
        }

    monkeypatch.setattr("backend.agents.nodes.resolve_entity.resolve_entity", _mock_resolve)
    monkeypatch.setattr("backend.agents.nodes.vector_search_node.vector_search", _mock_vector_search)
    monkeypatch.setattr("backend.agents.nodes.rank_results.keyword_search", _mock_keyword_search)
    monkeypatch.setattr("backend.agents.nodes.synthesize.llm_json_call", _mock_llm)

    result = await run_agent("account_brief", "show hiring signals for Acme")
    timeline = result.get("final_response", {}).get("signal_timeline", [])

    assert len(timeline) == 2
    assert timeline[0].get("detected_at") is not None
    assert timeline[0].get("source_url")


@pytest.mark.asyncio
async def test_enrichment_write_back(db_pool, monkeypatch):
    monkeypatch.setattr("backend.agents.router.get_pool", lambda: db_pool)
    monkeypatch.setattr("backend.agents.crm_enrichment.get_pool", lambda: db_pool)

    async def _mock_resolve(_: str):
        return None

    monkeypatch.setattr("backend.agents.crm_enrichment.resolve_entity", _mock_resolve)

    leads = [
        {"company": "Acme A", "name": "Alice One", "title": "AE"},
        {"company": "Acme B", "name": "Bob Two", "title": "SDR"},
        {"company": "Acme C", "name": "Cara Three", "title": "VP Sales"},
    ]
    await run_agent("crm_enrichment", "enrich this lead list", lead_list=leads)

    async with db_pool.acquire() as conn:
        people_count = await conn.fetchval("SELECT COUNT(*)::int FROM people")

    assert people_count == 3


@pytest.mark.asyncio
async def test_citation_validator_warns():
    response = {
        "facts": [{"claim": "Acme raised money", "citations": []}],
        "people": [{"full_name": "Jane", "citations": [{"url": "https://example.com"}]}],
    }
    warnings = validate_citations(response)
    assert warnings


@pytest.mark.asyncio
async def test_agent_router_keyword_classification():
    assert await classify_intent("find senior engineers at Acme") == "lead_finder"
    assert await classify_intent("show hiring signals for Acme") == "account_brief"
    assert await classify_intent("why is this record stale") == "ops_debug"
