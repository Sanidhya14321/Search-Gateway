---
name: citation-structured-response
description: >
  Format LLM synthesis output into structured CRMind responses with traceable
  source citations. Use this skill when attaching source links to facts, building
  the canonical JSON response shape, formatting citation cards, or ensuring every
  claim in the response is backed by a source URL with metadata. Keywords: citation,
  source link, structured response, fact attribution, evidence, response formatting,
  citation card, source traceability, audit trail.
---

## Principle

**Every claim in a CRMind response must have ≥1 source citation.**

The LLM synthesizes from retrieved context. The citation formatter maps claims
back to the chunks that supported them and attaches the source URL, fetch date,
trust score, and a short excerpt.

---

## Citation Data Model

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Citation(BaseModel):
    source_id: str              # chunk.id or source_doc.id
    url: str                    # original page URL
    source_type: str            # "news_article" | "linkedin" | etc.
    domain: str
    title: Optional[str]        # page title if available
    fetched_at: datetime
    trust_score: float
    freshness_score: float
    excerpt: str                # short supporting text snippet (≤200 chars)
    relevance_score: float      # how closely this chunk supports the claim

class CitedFact(BaseModel):
    fact_id: str
    claim: str                  # the factual claim being made
    confidence: float
    citations: List[Citation]   # ≥1 source per fact

class CitedPerson(BaseModel):
    canonical_id: str
    full_name: str
    current_title: Optional[str]
    seniority_level: str
    confidence: float
    citations: List[Citation]

class CitedSignal(BaseModel):
    signal_type: str
    description: str
    confidence: float
    impact_score: float
    event_date: Optional[str]
    citations: List[Citation]
```

---

## Citation Formatter

```python
from typing import List
import re

def format_citations_for_response(
    synthesis_output: dict,
    ranked_chunks: List[dict],
) -> dict:
    """
    Takes raw LLM synthesis output and matched chunks.
    Attaches citations to each fact/person/signal in the response.
    Returns enhanced response dict with full citation objects.
    """
    chunk_map = {c["id"]: c for c in ranked_chunks}

    # Format facts with citations
    cited_facts = []
    for fact in synthesis_output.get("facts", []):
        matched_chunks = find_supporting_chunks(fact["claim"], ranked_chunks, top_k=3)
        cited_facts.append(CitedFact(
            fact_id=f"fact_{len(cited_facts):03d}",
            claim=fact["claim"],
            confidence=fact.get("confidence", 0.5),
            citations=[build_citation(c) for c in matched_chunks],
        ))

    # Format people with citations
    cited_people = []
    for person in synthesis_output.get("people", []):
        matched_chunks = find_supporting_chunks(
            f"{person.get('name', '')} {person.get('title', '')}",
            ranked_chunks, top_k=2
        )
        cited_people.append(CitedPerson(
            canonical_id=person.get("canonical_id", ""),
            full_name=person.get("name", ""),
            current_title=person.get("title"),
            seniority_level=person.get("seniority", "unknown"),
            confidence=person.get("confidence", 0.5),
            citations=[build_citation(c) for c in matched_chunks],
        ))

    return {
        **synthesis_output,
        "facts":   [f.dict() for f in cited_facts],
        "people":  [p.dict() for p in cited_people],
        "citation_count": len(cited_facts) + len(cited_people),
    }
```

---

## Supporting Chunk Finder

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

async def find_supporting_chunks(
    claim: str,
    chunks: List[dict],
    top_k: int = 3,
) -> List[dict]:
    """
    Find which chunks best support a given claim.
    Uses embedding similarity between claim and chunk text.
    """
    if not chunks:
        return []

    claim_embedding = await embed(claim)
    claim_vec = np.array(claim_embedding).reshape(1, -1)

    scored = []
    for chunk in chunks:
        if chunk.get("embedding"):
            chunk_vec = np.array(chunk["embedding"]).reshape(1, -1)
            sim = cosine_similarity(claim_vec, chunk_vec)[0][0]
        else:
            # Fallback: keyword overlap score
            claim_words = set(claim.lower().split())
            chunk_words = set(chunk["chunk_text"].lower().split())
            sim = len(claim_words & chunk_words) / max(len(claim_words), 1)

        scored.append((sim, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]
```

---

## Citation Builder

```python
def build_citation(chunk: dict) -> Citation:
    excerpt = chunk["chunk_text"][:200].strip()
    if len(chunk["chunk_text"]) > 200:
        excerpt += "…"

    return Citation(
        source_id=chunk["id"],
        url=chunk.get("source_url", ""),
        source_type=chunk.get("source_type", "unknown"),
        domain=extract_domain(chunk.get("source_url", "")),
        title=chunk.get("page_title"),
        fetched_at=chunk["fetched_at"],
        trust_score=chunk.get("trust_score", 0.5),
        freshness_score=chunk.get("freshness_score", 0.5),
        excerpt=excerpt,
        relevance_score=chunk.get("final_score", 0.5),
    )

def extract_domain(url: str) -> str:
    from urllib.parse import urlparse
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""
```

---

## Final Response Assembler

```python
from datetime import datetime, timezone

def assemble_final_response(
    entity: dict,
    synthesis: dict,
    cited_facts: List[CitedFact],
    cited_people: List[CitedPerson],
    signals: List[CitedSignal],
    resolution_confidence: float,
) -> dict:
    """
    Assemble the canonical CRMind response shape.
    """
    all_citations = []
    for f in cited_facts:
        all_citations.extend(f.citations)
    for p in cited_people:
        all_citations.extend(p.citations)

    # Deduplicate citations by source URL
    seen_urls = set()
    unique_citations = []
    for c in all_citations:
        if c.url not in seen_urls:
            unique_citations.append(c)
            seen_urls.add(c.url)

    return {
        "entity_id":        entity.get("canonical_id"),
        "entity_type":      entity.get("entity_type"),
        "canonical_name":   entity.get("canonical_name"),
        "confidence":       resolution_confidence,
        "summary":          synthesis.get("summary"),
        "facts":            [f.dict() for f in cited_facts],
        "signals":          [s.dict() for s in signals],
        "people":           [p.dict() for p in cited_people],
        "citations":        [c.dict() for c in unique_citations],
        "citation_count":   len(unique_citations),
        "retrieved_at":     datetime.now(timezone.utc).isoformat(),
        "pipeline_version": "1.0.0",
    }
```

---

## Citation Validation

```python
def validate_citations(response: dict) -> list[str]:
    """
    Quality check: every fact and person must have ≥1 citation.
    Returns list of warnings.
    """
    warnings = []
    for fact in response.get("facts", []):
        if not fact.get("citations"):
            warnings.append(f"Uncited fact: '{fact['claim'][:60]}...'")
    for person in response.get("people", []):
        if not person.get("citations"):
            warnings.append(f"Uncited person: {person['full_name']}")
    return warnings
```

---

## File locations

```
backend/
  services/
    citations/
      formatter.py        ← format_citations_for_response
      builder.py          ← build_citation, extract_domain
      finder.py           ← find_supporting_chunks
      assembler.py        ← assemble_final_response
      validator.py        ← validate_citations
  tests/
    test_citations.py
```