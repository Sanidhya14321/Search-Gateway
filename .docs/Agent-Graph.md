# CRMind — Agent Graph Specification

All agents are implemented as LangGraph `StateGraph` instances.
Each node is a Python function; edges are conditional or direct.
All agents share the `BaseAgentState` and call tools — they never answer from memory.

---

## Shared State Schema

```python
from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END

class BaseAgentState(TypedDict):
    query: str
    entity_id: Optional[str]
    entity_type: Optional[str]           # "company" | "person" | "account"
    resolved_entity: Optional[dict]
    retrieved_chunks: List[dict]
    ranked_chunks: List[dict]
    tool_calls: List[dict]
    final_response: Optional[dict]
    citations: List[dict]
    confidence: float
    error: Optional[str]
    steps_log: List[str]
```

---

## Workflow A — Lead Finder Agent

**Trigger:** "Find senior engineers at Company X"

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEAD FINDER AGENT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [START]                                                        │
│     │                                                           │
│     ▼                                                           │
│  parse_query                                                    │
│  (extract company name, title filter, seniority filter)         │
│     │                                                           │
│     ▼                                                           │
│  resolve_company_entity                                         │
│  (fuzzy match → canonical company_id)                           │
│     │                                                           │
│     ├── NOT FOUND ──► ask_clarification ──► [END with error]   │
│     │                                                           │
│     ▼                                                           │
│  search_people_db                                               │
│  (filter: company_id, seniority, title keywords)                │
│     │                                                           │
│     ▼                                                           │
│  vector_search_people                                           │
│  (embed query → cosine search in chunks table)                  │
│     │                                                           │
│     ▼                                                           │
│  merge_and_deduplicate                                          │
│  (canonical_id dedup, merge role info)                          │
│     │                                                           │
│     ▼                                                           │
│  verify_with_sources                                            │
│  (for each person: attach source_urls, confidence)              │
│     │                                                           │
│     ├── low confidence ──► trigger_live_crawl (optional)       │
│     │                                                           │
│     ▼                                                           │
│  rank_results                                                   │
│  (score = 0.4×sim + 0.25×freshness + 0.2×trust + 0.15×auth)   │
│     │                                                           │
│     ▼                                                           │
│  synthesize_response                                            │
│  (LLM call with retrieved context, not from memory)             │
│     │                                                           │
│     ▼                                                           │
│  format_with_citations                                          │
│  (attach source_url, fetched_at, excerpt per person)            │
│     │                                                           │
│     ▼                                                           │
│  [END — return structured JSON]                                 │
└─────────────────────────────────────────────────────────────────┘
```

**LangGraph Definition:**
```python
lead_finder = StateGraph(LeadFinderState)
lead_finder.add_node("parse_query",            parse_query_node)
lead_finder.add_node("resolve_company",        resolve_company_node)
lead_finder.add_node("search_people_db",       search_people_db_node)
lead_finder.add_node("vector_search_people",   vector_search_node)
lead_finder.add_node("merge_dedup",            merge_dedup_node)
lead_finder.add_node("verify_sources",         verify_sources_node)
lead_finder.add_node("rank_results",           rank_results_node)
lead_finder.add_node("synthesize",             synthesize_node)
lead_finder.add_node("format_citations",       format_citations_node)

lead_finder.set_entry_point("parse_query")
lead_finder.add_edge("parse_query",           "resolve_company")
lead_finder.add_conditional_edges("resolve_company", route_resolved,
  {"found": "search_people_db", "not_found": END})
lead_finder.add_edge("search_people_db",      "vector_search_people")
lead_finder.add_edge("vector_search_people",  "merge_dedup")
lead_finder.add_edge("merge_dedup",           "verify_sources")
lead_finder.add_edge("verify_sources",        "rank_results")
lead_finder.add_edge("rank_results",          "synthesize")
lead_finder.add_edge("synthesize",            "format_citations")
lead_finder.add_edge("format_citations",      END)
```

---

## Workflow B — Account Brief Generator

**Trigger:** "Give me a brief on Company Y" / "Show hiring signals for Acme"

```
┌─────────────────────────────────────────────────────────────────┐
│                  ACCOUNT BRIEF AGENT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [START]                                                        │
│     │                                                           │
│     ▼                                                           │
│  resolve_entity                                                 │
│     │                                                           │
│     ▼                                                           │
│  fetch_recent_signals          ◄─── signals table (last 90d)   │
│     │                                                           │
│     ▼                                                           │
│  fetch_source_documents        ◄─── company news + blog + jobs  │
│     │                                                           │
│     ▼                                                           │
│  fetch_people_changes          ◄─── roles with recent start_date│
│     │                                                           │
│     ▼                                                           │
│  vector_search_context                                          │
│  (embed: "company overview + recent events")                    │
│     │                                                           │
│     ▼                                                           │
│  rank_by_freshness_and_signal                                   │
│  (prioritise signals: funding > hiring > product)               │
│     │                                                           │
│     ▼                                                           │
│  synthesize_brief                                               │
│  (LLM: "Why does this matter for sales?" prompt)               │
│     │                                                           │
│     ▼                                                           │
│  format_timeline_with_citations                                 │
│  (chronological event list + source per event)                  │
│     │                                                           │
│     ▼                                                           │
│  [END — account_brief JSON + signal_timeline]                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow C — CRM Enrichment Agent

**Trigger:** Upload CSV / pass list of leads

```
┌─────────────────────────────────────────────────────────────────┐
│                  CRM ENRICHMENT AGENT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [START — receives lead_list: List[dict]]                       │
│     │                                                           │
│     ▼                                                           │
│  validate_input_schema                                          │
│  (check required fields: name or domain)                        │
│     │                                                           │
│     ▼                                                           │
│  batch_entity_resolution         ◄── runs per row, parallel    │
│  (for each lead → resolve company + person canonical_id)        │
│     │                                                           │
│     ▼                                                           │
│  check_existing_records                                         │
│  (lookup DB: avoid re-enriching fresh records)                  │
│     │                                                           │
│     ▼                                                           │
│  enrich_missing_fields                                          │
│  (for stale/missing → pull from source_docs, facts table)       │
│     │                                                           │
│     ▼                                                           │
│  flag_low_confidence_rows                                       │
│  (confidence < 0.6 → mark for human review)                     │
│     │                                                           │
│     ▼                                                           │
│  deduplicate_output                                             │
│  (canonical_id dedup within the batch)                          │
│     │                                                           │
│     ▼                                                           │
│  write_back_to_db                                               │
│  (upsert people, companies, roles tables)                       │
│     │                                                           │
│     ▼                                                           │
│  generate_enrichment_report                                     │
│  (rows enriched, rows flagged, rows failed, fields added)       │
│     │                                                           │
│     ▼                                                           │
│  [END — enriched_csv + report JSON]                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow D — Research Agent

**Trigger:** "Research the competitive landscape in AI infrastructure"

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH AGENT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [START]                                                        │
│     │                                                           │
│     ▼                                                           │
│  decompose_query                                                │
│  (break into 3-5 sub-questions for parallel retrieval)          │
│     │                                                           │
│     ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐      │
│  │         PARALLEL RETRIEVAL (per sub-question)        │      │
│  │                                                      │      │
│  │   vector_search ──► rank ──► top_k_chunks            │      │
│  │   keyword_search ──► rank ──► top_k_sources          │      │
│  │   signal_lookup  ──► rank ──► relevant_signals       │      │
│  └──────────────────────────────────────────────────────┘      │
│     │                                                           │
│     ▼                                                           │
│  merge_all_evidence                                             │
│  (deduplicate across sub-questions, assign source labels)       │
│     │                                                           │
│     ▼                                                           │
│  rank_by_trust_and_freshness                                    │
│     │                                                           │
│     ▼                                                           │
│  synthesize_report_sections                                     │
│  (LLM: generate each section grounded on retrieved chunks)      │
│     │                                                           │
│     ▼                                                           │
│  assemble_report_card                                           │
│  (title + sections + citations + confidence per section)        │
│     │                                                           │
│     ▼                                                           │
│  [END — research_report JSON]                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow E — Ops / Debug Agent

**Trigger:** "Why is this record stale?" / "Why did the crawl fail for acme.com?"

```
┌─────────────────────────────────────────────────────────────────┐
│                      OPS AGENT                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [START]                                                        │
│     │                                                           │
│     ▼                                                           │
│  identify_subject                                               │
│  (entity_id or domain from query)                               │
│     │                                                           │
│     ▼                                                           │
│  inspect_entity_freshness                                       │
│  (check updated_at, freshness_score, last crawl)                │
│     │                                                           │
│     ▼                                                           │
│  check_crawl_queue_status                                       │
│  (pending? failed? retries exhausted?)                          │
│     │                                                           │
│     ▼                                                           │
│  inspect_pipeline_logs                                          │
│  (last 5 agent_runs for this entity)                            │
│     │                                                           │
│     ▼                                                           │
│  identify_failure_cause                                         │
│  (HTTP error? robots.txt block? entity mismatch? no sources?)   │
│     │                                                           │
│     ▼                                                           │
│  generate_remediation_steps                                     │
│  (LLM: suggest fix given failure context)                       │
│     │                                                           │
│     ├── auto-fixable ──► apply_fix (re-queue, re-resolve)      │
│     │                                                           │
│     └── needs human ──► flag_for_review                        │
│     │                                                           │
│     ▼                                                           │
│  [END — ops_report JSON with cause + steps]                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Shared Tool Registry

All agents call tools from this registry (never answer from memory):

```python
TOOL_REGISTRY = {
    # Retrieval tools
    "vector_search":         vector_search_tool,         # pgvector cosine
    "keyword_search":        keyword_search_tool,         # pg full-text / trgm
    "get_entity":            get_entity_tool,             # fetch canonical entity
    "get_signals":           get_signals_tool,            # fetch signals by entity
    "get_facts":             get_facts_tool,              # fetch facts by entity
    "get_sources":           get_sources_tool,            # fetch source_docs

    # Enrichment tools
    "resolve_entity":        resolve_entity_tool,         # fuzzy match → canonical
    "enrich_company":        enrich_company_tool,         # pull + store company data
    "enrich_person":         enrich_person_tool,          # pull + store person data

    # Crawl tools
    "crawl_url":             crawl_url_tool,              # trigger sync crawl
    "queue_crawl":           queue_crawl_tool,            # add to async queue
    "get_crawl_status":      get_crawl_status_tool,       # check queue item

    # Pipeline tools
    "get_pipeline_logs":     get_pipeline_logs_tool,      # fetch agent_runs logs
    "compute_freshness":     compute_freshness_tool,      # recalculate scores
    "flag_for_review":       flag_for_review_tool,        # mark entity

    # Output tools
    "format_citations":      format_citations_tool,       # attach sources to facts
    "generate_summary":      generate_summary_tool,       # LLM-backed synthesis
}
```

---

## Agent Router

Entry point that dispatches incoming queries to the right workflow:

```
User Query
    │
    ▼
┌───────────────────────────────────────────┐
│           AGENT ROUTER                    │
│                                           │
│  classify_intent()                        │
│    ├── "find people"     → LEAD_FINDER    │
│    ├── "account/company" → ACCOUNT_BRIEF  │
│    ├── "enrich/upload"   → CRM_ENRICHMENT │
│    ├── "research/market" → RESEARCH       │
│    └── "debug/stale/ops" → OPS_DEBUG      │
└───────────────────────────────────────────┘
```