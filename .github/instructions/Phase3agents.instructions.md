---
description: Load when working on LangGraph agents, agent nodes, agent state, agent router, citation formatting, or any Phase 3 agent workflow tasks.
applyTo: "{backend/agents/**,backend/services/citations/**,backend/routers/agents.py,tests/test_phase3.py}"
---

# Phase 3 — Agent Workflows: LangGraph Agents + Structured Responses

## Goal
All 5 LangGraph agents working, grounded in retrieval, returning canonical
JSON responses with traceable citations. Agent runs logged to `agent_runs` table.

## Checklist
- [ ] 3.1 `CRMindState` TypedDict + `llm_client.py`
- [ ] 3.2 Shared agent nodes
- [ ] 3.3 Lead Finder agent
- [ ] 3.4 Account Brief agent
- [ ] 3.5 CRM Enrichment agent
- [ ] 3.6 Research + Ops/Debug agents
- [ ] 3.7 Agent router (`run_agent`, `classify_intent`)
- [ ] 3.8 Citation formatter (full `services/citations/` module)
- [ ] 3.9 `POST /api/v1/agent/run` + `GET /api/v1/agent/run/{run_id}`
- [ ] 3.10 Phase 3 tests passing

## Step-by-Step Copilot Prompts

### 3.1 — Agent state and LLM client
```
#file:.agents/skills/langgraph-agent-workflows/SKILL.md
@workspace Implement backend/agents/state.py with CRMindState TypedDict:
fields: query, entity_id, entity_type, resolved_entity, resolution_confidence,
retrieved_chunks, ranked_chunks, tool_calls, steps_log, iteration_count,
final_response, citations, error.
All list fields default to []. All optional fields default to None.

Implement backend/agents/llm_client.py with async llm_json_call(prompt, system="", model=None):
- Primary mode: call Groq chat completions (JSON response format)
- Fallback mode: call OpenAI chat completions if primary fails
- Strip ```json fences before JSON.loads()
- On parse failure: log the raw response and raise ValueError with the raw text
- model defaults to settings.groq_llm_model with OpenAI fallback model override
```

### 3.2 — Shared nodes
```
#file:.agents/skills/langgraph-agent-workflows/SKILL.md
@workspace Implement these node functions in backend/agents/nodes/:
parse_query_node(state) — LLM extracts: company_name, title_keywords[], seniority
  Returns: {_parsed_filters: dict, steps_log: [...+entry]}

resolve_entity_node(state) — calls entity_resolver.resolve_entity()
  Returns: {resolved_entity, entity_id, resolution_confidence, steps_log}

vector_search_node(state) — calls retrieval.vector_search() with entity context
  Returns: {retrieved_chunks, steps_log}

rank_results_node(state) — calls merger.merge + ranker.rank_chunks
  Returns: {ranked_chunks, steps_log}

synthesize_node(state) — MUST use ranked_chunks as context, never model memory
  System prompt must say: "Answer ONLY using provided source context."
  Returns: {final_response: dict, steps_log}

format_citations_node(state) — calls citations.formatter.format_citations_for_response
  Returns: {citations, final_response (enhanced), steps_log}

Each node appends a log entry to steps_log in format: "[node_name] description"
```

### 3.3 — Lead Finder agent
```
#file:.agents/skills/langgraph-agent-workflows/SKILL.md
@workspace Implement backend/agents/lead_finder.py with build_lead_finder_graph():
Nodes in order: parse_query → resolve_company → search_people_db →
vector_search → merge_dedup → verify_sources → rank_results → synthesize → format_citations

search_people_db_node: SELECT from people JOIN roles WHERE company_id=$1
  AND ($2 IS NULL OR seniority_level = $2::seniority_level)
  Filter title by _parsed_filters.title_keywords using ILIKE ANY

merge_dedup_node: combine DB people results + vector_search chunk results,
  deduplicate by canonical_id, merge source evidence

Conditional edge after resolve_company:
  resolution_confidence ≥ 0.6 → search_people_db
  resolution_confidence < 0.6 → END with error = "Entity not resolved"

Add graph to WORKFLOW_REGISTRY in router.py.
```

### 3.4 — Account Brief agent
```
#file:.agents/skills/langgraph-agent-workflows/SKILL.md
@workspace Implement backend/agents/account_brief.py with build_account_brief_graph():
Nodes: resolve_entity → fetch_signals → fetch_people_changes →
vector_search → rank_results → synthesize_brief → format_citations

fetch_signals_node: SELECT from signals WHERE entity_id=$1
  AND detected_at > NOW() - INTERVAL '90 days' ORDER BY detected_at DESC

fetch_people_changes_node: SELECT from people JOIN roles WHERE company_id=$1
  AND roles.start_date > NOW() - INTERVAL '180 days'

synthesize_brief_node: LLM prompt must include:
  "Explain why this matters for a sales team reaching out to this account."
  Output must include: summary, signal_timeline[], key_people[], why_reach_out_now

Add graph to WORKFLOW_REGISTRY.
```

### 3.5 — CRM Enrichment agent
```
#file:.agents/skills/langgraph-agent-workflows/SKILL.md
@workspace Implement backend/agents/crm_enrichment.py with build_crm_enrichment_graph():
Input state must accept lead_list: List[dict] in addition to standard fields.
Nodes: validate_input → batch_resolve → check_existing → enrich_missing →
  flag_low_confidence → deduplicate_batch → write_back → generate_report

batch_resolve_node: run resolve_entity() for each lead concurrently with asyncio.gather()
  max 10 concurrent resolutions

check_existing_node: for resolved entities, fetch freshness_score from DB;
  skip enrichment if freshness_score > 0.7

write_back_node: asyncpg executemany upsert on people + companies + roles
  Use ON CONFLICT (canonical_id) DO UPDATE

generate_report_node: return {
  total: N, enriched: N, skipped_fresh: N, flagged_low_confidence: N,
  failed: N, fields_added: [...], warnings: [...]
}
```

### 3.6 — Research + Ops agents
```
#file:.agents/skills/langgraph-agent-workflows/SKILL.md
@workspace Implement:

backend/agents/research.py — build_research_graph():
  decompose_query_node: LLM breaks query into 3-5 sub-questions (JSON array)
  parallel_retrieval_node: asyncio.gather() vector_search for each sub-question
  merge_all_evidence_node: flatten + deduplicate chunks across sub-questions
  synthesize_report_node: LLM generates sections, one per sub-question
  assemble_report_card_node: {title, sections[{heading,content,citations}], confidence}

backend/agents/ops_debug.py — build_ops_debug_graph():
  identify_subject_node: extract entity_id or domain from query
  inspect_freshness_node: SELECT freshness_score, updated_at from entity table
  check_crawl_queue_node: SELECT status, attempts, error_message from crawl_queue
  inspect_pipeline_logs_node: SELECT last 5 agent_runs for this entity
  identify_failure_cause_node: LLM classifies failure type from logs
  generate_remediation_node: LLM suggests fix; if auto_fixable → re-queue crawl

Add both graphs to WORKFLOW_REGISTRY.
```

### 3.7 — Agent router
```
@workspace Implement backend/agents/router.py:
WORKFLOW_REGISTRY: dict mapping name → compiled graph
  keys: "lead_finder","account_brief","crm_enrichment","research","ops_debug"

async classify_intent(query: str) → str:
  Rule-based first (keyword matching, fast):
    "find * at" / "people at" / "engineers at" → lead_finder
    "brief" / "signals" / "hiring" / "summary" → account_brief
    "enrich" / "csv" / "lead list" → crm_enrichment
    "research" / "market" / "landscape" → research
    "why" / "stale" / "failed" / "debug" → ops_debug
  Fall back to LLM classification if no keyword match.

async run_agent(workflow_name, query, **kwargs) → dict:
  Build initial CRMindState, invoke graph, log to agent_runs table.
  Record start in agent_runs before invoke, update status after.
```

### 3.8 — Citation module
```
#file:.agents/skills/citation-structured-response/SKILL.md
@workspace Implement backend/services/citations/ with these files:
builder.py — build_citation(chunk) → Citation, extract_domain(url)
finder.py — async find_supporting_chunks(claim, chunks, top_k=3)
  cosine similarity between claim embedding and chunk embeddings
  fallback to keyword overlap if no embeddings
formatter.py — format_citations_for_response(synthesis_output, ranked_chunks)
  Attach Citation objects to each fact and each person in the response
assembler.py — assemble_final_response(entity, synthesis, cited_facts, cited_people, signals, confidence)
  Deduplicates citations by URL, returns canonical response shape
validator.py — validate_citations(response) → List[str] warnings
  Warn for any fact or person with 0 citations
```

### 3.9 — Agent API endpoints
```
#file:.agents/skills/fastapi-backend-structure/SKILL.md
@workspace Implement backend/routers/agents.py:
POST /api/v1/agent/run
  Body: AgentRunRequest{workflow_name, query, entity_id?, entity_type?, lead_list?}
  1. Generate run_id (UUID)
  2. INSERT agent_runs with status=running
  3. Call run_agent()
  4. UPDATE agent_runs with status, output, duration_ms
  5. Return AgentRunResponse{run_id, workflow_name, status, result, steps_log, citations, duration_ms}
  6. On exception: UPDATE status=failed, error_message; re-raise as HTTP 500

GET /api/v1/agent/run/{run_id}
  SELECT from agent_runs by run_id
  Return AgentRunResponse (result may be null if status=running)
```

### 3.10 — Phase 3 tests
```
@workspace Create tests/test_phase3.py using pytest-asyncio + unittest.mock.AsyncMock:
- test_lead_finder_happy_path:
    mock resolve_entity → confidence 0.95
    mock vector_search → 3 chunks with source URLs
    mock llm_json_call → {people:[...], facts:[...], summary:"..."}
    assert output has people[], citations[], each person has ≥1 citation URL

- test_lead_finder_entity_not_found:
    mock resolve_entity → confidence 0.3
    assert final state has error != None, people == []

- test_account_brief_has_signals:
    seed 2 signals in DB, run account_brief agent
    assert signal_timeline has 2 entries with detected_at and source_url

- test_enrichment_write_back:
    input 3 leads, mock resolution + retrieval
    assert 3 rows upserted in people table

- test_citation_validator_warns:
    response with one fact missing citations
    validate_citations() returns non-empty warnings list

- test_agent_router_keyword_classification:
    classify_intent("find senior engineers at Acme") → "lead_finder"
    classify_intent("show hiring signals for Acme") → "account_brief"
    classify_intent("why is this record stale") → "ops_debug"

Never call real LLM or real crawler in tests. Mock at the service boundary.
```

## Core Anti-Patterns — Block These in Code Review

```python
# NEVER — LLM answering from training memory
response = await llm("What do you know about Acme Corp?")

# NEVER — synthesis without retrieved context
async def synthesize_node(state):
    return {"final_response": await llm(state["query"])}   # ❌ no context passed

# NEVER — returning response without citations
return {"facts": [{"claim": "Acme raised $10M"}]}   # ❌ missing citations key

# ALWAYS — retrieve first, ground synthesis
context = assemble_context(state["ranked_chunks"])
response = await llm_json_call(f"Context:\n{context}\nQuery: {state['query']}")
```

## Definition of Done

`POST /api/v1/agent/run` with `{"workflow_name":"lead_finder","query":"Find engineers at Example Inc"}` returns a response where every person in `people[]` has at least one entry in `citations[]` with a non-empty `url`.
`pytest tests/test_phase3.py` passes with all LLM calls mocked.