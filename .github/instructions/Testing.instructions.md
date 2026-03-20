---
description: Load when writing any type of test — unit, integration, e2e, contract, or load. Covers conftest fixtures, mocking strategy, test database setup, and CI test ordering.
applyTo: "{tests/**,conftest.py,pytest.ini}"
---

# Testing — Quick Reference

Full patterns in: `#file:.agents/skills/testing/SKILL.md`

## Test Types & When to Use Each

| Type | DB? | LLM mock? | HTTP mock? | Run in CI? |
|------|-----|-----------|------------|-----------|
| unit | No | Yes | Yes | Yes (first) |
| integration | Real test DB | Yes | Yes | Yes |
| e2e | Real test DB | Yes | No | Yes |
| contract | Real test DB | Yes | No | Yes |
| load | No (optional) | No | No | Manual only |

## The 3 Non-Negotiables

1. **Never call real LLM in tests.** Use `mock_llm` fixture.
2. **Never call real URLs.** Use `mock_crawler` fixture.
3. **Every test is independently runnable.** `clean_tables` autouse fixture handles this.

## Mock Imports

```python
from tests.conftest import mock_llm, mock_embed, mock_crawler
# OR just declare as params — pytest auto-injects from conftest.py
async def test_something(client, seeded_company, mock_llm, mock_embed):
```

## Assert on Shape, Not Text

```python
# WRONG — LLM output is non-deterministic
assert result["summary"] == "Test Inc is a SaaS company"

# RIGHT — assert structure and required fields
assert result["summary"] is not None and len(result["summary"]) > 0
for person in result["people"]:
    assert len(person["citations"]) >= 1, f"{person['full_name']} has no citation"
    assert person["citations"][0]["url"] != ""
```

## CI Order

```bash
pytest tests/unit/ -m unit -v          # fast, first
pytest tests/integration/ -m integration
pytest tests/e2e/ -m e2e
pytest tests/contract/ -m contract
pytest tests/ --ignore=tests/load --cov=backend --cov-report=xml
```

## Coverage Minimums

- `backend/services/` : 80%
- `backend/scoring/`  : 90%
- `backend/agents/`   : 70%
- `backend/crawler/`  : 70%