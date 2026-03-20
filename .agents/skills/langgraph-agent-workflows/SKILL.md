---
name: langgraph-agent-workflows
description: >
  Implement LangGraph-based tool-calling agent workflows for CRMind. Use this skill
  when building or modifying any agent: Lead Finder, Account Brief, CRM Enrichment,
  Research, or Ops/Debug. Covers StateGraph setup, node functions, conditional edges,
  tool binding, and structured output. Keywords: LangGraph, agent, StateGraph,
  tool calling, agent workflow, node, edge, conditional routing, agent state,
  lead finder, account brief, enrichment agent.
---

## Core Pattern

Every CRMind agent follows this pattern:

1. **State** — TypedDict that flows through all nodes
2. **Nodes** — pure async functions `(state) -> state_update`
3. **Tools** — called inside nodes, never from memory
4. **Edges** — direct or conditional routing between nodes
5. **Output** — always structured JSON with citations

---

## Base State

```python
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages

class CRMindState(TypedDict):
    # Input
    query: str
    entity_id: Optional[str]
    entity_type: Optional[str]

    # Resolution
    resolved_entity: Optional[dict]
    resolution_confidence: float

    # Retrieval
    retrieved_chunks: List[dict]
    ranked_chunks: List[dict]

    # Agent tracking
    tool_calls: List[dict]
    steps_log: List[str]
    iteration_count: int

    # Output
    final_response: Optional[dict]
    citations: List[dict]
    error: Optional[str]
```

---

## Node Template

```python
async def my_node(state: CRMindState) -> dict:
    """
    Each node receives the full state, returns a PARTIAL update dict.
    Only return keys you want to change.
    """
    # 1. Read from state
    query = state["query"]

    # 2. Call a tool (never answer from memory)
    result = await some_tool(query)

    # 3. Log the step
    log_entry = f"[my_node] processed query: {query[:50]}"

    # 4. Return partial state update
    return {
        "retrieved_chunks": result.chunks,
        "steps_log": state["steps_log"] + [log_entry],
        "iteration_count": state.get("iteration_count", 0) + 1,
    }
```

---

## Lead Finder Agent

```python
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

def build_lead_finder_graph() -> StateGraph:
    graph = StateGraph(CRMindState)

    graph.add_node("parse_query",          parse_query_node)
    graph.add_node("resolve_company",      resolve_company_node)
    graph.add_node("search_people_db",     search_people_db_node)
    graph.add_node("vector_search",        vector_search_node)
    graph.add_node("merge_dedup",          merge_dedup_node)
    graph.add_node("verify_sources",       verify_sources_node)
    graph.add_node("rank_results",         rank_results_node)
    graph.add_node("synthesize",           synthesize_node)
    graph.add_node("format_citations",     format_citations_node)

    graph.add_edge(START, "parse_query")
    graph.add_edge("parse_query",          "resolve_company")
    graph.add_conditional_edges(
        "resolve_company",
        lambda s: "found" if s["resolution_confidence"] > 0.6 else "not_found",
        {"found": "search_people_db", "not_found": END}
    )
    graph.add_edge("search_people_db",     "vector_search")
    graph.add_edge("vector_search",        "merge_dedup")
    graph.add_edge("merge_dedup",          "verify_sources")
    graph.add_edge("verify_sources",       "rank_results")
    graph.add_edge("rank_results",         "synthesize")
    graph.add_edge("synthesize",           "format_citations")
    graph.add_edge("format_citations",     END)

    return graph.compile()
```

---

## Node Implementations

### parse_query_node

```python
async def parse_query_node(state: CRMindState) -> dict:
    """Extract company name, title filter, seniority filter from the query."""
    prompt = f"""
    Extract from this query:
    - company_name: the target company
    - title_keywords: list of job title keywords (empty list if none)
    - seniority: one of [intern, junior, mid, senior, staff, principal, director, vp, c_level, any]
    
    Query: {state["query"]}
    
    Return JSON only.
    """
    result = await llm_json_call(prompt)
    return {
        "entity_type": "company",
        "steps_log": state["steps_log"] + [f"Parsed query: {result}"],
        "_parsed_filters": result,   # store in metadata
    }
```

### resolve_company_node

```python
async def resolve_company_node(state: CRMindState) -> dict:
    from services.entity_resolver import resolve_entity
    filters = state.get("_parsed_filters", {})
    company_name = filters.get("company_name", state["query"])

    resolved = await resolve_entity(company_name, entity_type="company")
    return {
        "resolved_entity": resolved.record if resolved else None,
        "entity_id": resolved.canonical_id if resolved else None,
        "resolution_confidence": resolved.confidence if resolved else 0.0,
        "steps_log": state["steps_log"] + [
            f"Resolved entity: {resolved.canonical_id if resolved else 'NOT FOUND'} "
            f"(confidence={resolved.confidence if resolved else 0:.2f})"
        ],
    }
```

### synthesize_node

```python
async def synthesize_node(state: CRMindState) -> dict:
    """
    LLM synthesis. ALWAYS grounded on retrieved chunks.
    Never answer from model memory.
    """
    context = assemble_context(state["ranked_chunks"])
    entity_name = state["resolved_entity"]["canonical_name"] if state["resolved_entity"] else "the company"

    system_prompt = """
    You are a CRM intelligence assistant. 
    Answer ONLY using the provided source context.
    If the context doesn't contain the answer, say so explicitly.
    Do NOT use your training knowledge.
    Always reference which source supports each claim.
    """

    user_prompt = f"""
    Query: {state["query"]}
    
    Source context:
    {context}
    
    Return a JSON object with:
    - summary: 2-3 sentence overview
    - people: list of {{name, title, seniority, source_url, confidence}}
    - facts: list of {{claim, source_url, confidence}}
    """

    response = await llm_json_call(user_prompt, system=system_prompt)
    return {
        "final_response": response,
        "steps_log": state["steps_log"] + ["Synthesis complete"],
    }
```

---

## Agent Router

```python
WORKFLOW_REGISTRY = {
    "lead_finder":     build_lead_finder_graph(),
    "account_brief":   build_account_brief_graph(),
    "crm_enrichment":  build_crm_enrichment_graph(),
    "research":        build_research_graph(),
    "ops_debug":       build_ops_debug_graph(),
}

async def run_agent(workflow_name: str, query: str, **kwargs) -> dict:
    graph = WORKFLOW_REGISTRY[workflow_name]
    initial_state: CRMindState = {
        "query": query,
        "entity_id": kwargs.get("entity_id"),
        "entity_type": kwargs.get("entity_type"),
        "resolved_entity": None,
        "resolution_confidence": 0.0,
        "retrieved_chunks": [],
        "ranked_chunks": [],
        "tool_calls": [],
        "steps_log": [],
        "iteration_count": 0,
        "final_response": None,
        "citations": [],
        "error": None,
    }
    result = await graph.ainvoke(initial_state)
    return result
```

---

## LLM JSON Call Helper

```python
import json
from groq import AsyncGroq
from openai import AsyncOpenAI

groq_client = AsyncGroq(api_key=settings.groq_api_key)
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

async def llm_json_call_with_fallback(prompt: str, system: str = "") -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await groq_client.chat.completions.create(
            model=settings.groq_llm_model,
            response_format={"type": "json_object"},
            messages=messages,
        )
        text = response.choices[0].message.content
    except Exception:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=messages,
        )
        text = response.choices[0].message.content

    # Strip markdown fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("```")

    return json.loads(text)
```

---

## Anti-Patterns — Never Do These

```python
# ❌ WRONG — answering from model memory
async def bad_synthesize(state):
    response = await llm("What do you know about " + state["query"])
    return {"final_response": response}

# ✅ RIGHT — always retrieve first, then synthesize
async def good_synthesize(state):
    chunks = state["ranked_chunks"]       # must be populated by prior nodes
    context = assemble_context(chunks)
    response = await llm_json_call(f"Given this context:\n{context}\nAnswer: {state['query']}")
    return {"final_response": response}
```

---

## File locations

```
backend/
  agents/
    state.py              ← CRMindState TypedDict
    router.py             ← run_agent, WORKFLOW_REGISTRY
    lead_finder.py        ← build_lead_finder_graph + nodes
    account_brief.py
    crm_enrichment.py
    research.py
    ops_debug.py
    nodes/
      parse_query.py
      resolve_entity.py
      synthesize.py
      format_citations.py
    llm_client.py         ← llm_json_call
  tests/
    test_lead_finder.py
    test_account_brief.py
```