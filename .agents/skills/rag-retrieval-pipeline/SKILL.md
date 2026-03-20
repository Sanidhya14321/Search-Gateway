---
name: rag-retrieval-pipeline
description: >
  Implement the retrieval pipeline for CRMind: vector search, keyword search,
  metadata filtering, freshness ranking, trust scoring, and result merging.
  Use this skill when writing retrieval logic, chunk ranking, pgvector queries,
  similarity search, or any code that fetches context to ground LLM responses.
  Keywords: RAG, retrieval, vector search, pgvector, ranking, freshness, trust score,
  cosine similarity, hybrid search, chunk retrieval.
---

## Architecture

```
User Query
    │
    ├── embed(query) → vector
    ├── extract_keywords(query) → keyword list
    └── extract_filters(query) → entity_id, date_range, source_type
          │
          ▼
    ┌─────────────────────────────────┐
    │  PARALLEL RETRIEVAL             │
    │  vector_search()   top_k=20     │
    │  keyword_search()  top_k=20     │
    └─────────────────────────────────┘
          │
          ▼
    merge_results()        # RRF or score union
          │
          ▼
    apply_metadata_filters()
          │
          ▼
    score_and_rank()       # freshness × trust × similarity
          │
          ▼
    top_k_final(k=8)       # send to LLM context
```

---

## Vector Search (pgvector)

```python
async def vector_search(
    query: str,
    entity_id: str | None = None,
    entity_type: str | None = None,
    top_k: int = 20,
    min_similarity: float = 0.3,
) -> List[ChunkResult]:
    embedding = await embed(query)   # 768-dim vector

    sql = """
        SELECT
            c.id,
            c.chunk_text,
            c.source_doc_id,
            c.entity_id,
            c.freshness_score,
            c.trust_score,
            sd.source_url,
            sd.source_type,
            sd.fetched_at,
            1 - (c.embedding <=> $1::vector) AS similarity
        FROM chunks c
        JOIN source_documents sd ON sd.id = c.source_doc_id
        WHERE 1 - (c.embedding <=> $1::vector) > $2
          AND ($3::uuid IS NULL OR c.entity_id = $3)
          AND ($4::text IS NULL OR c.entity_type = $4::entity_type)
        ORDER BY c.embedding <=> $1::vector
        LIMIT $5
    """
    rows = await db.fetch(sql, embedding, min_similarity, entity_id, entity_type, top_k)
    return [ChunkResult(**row) for row in rows]
```

---

## Keyword Search (pg full-text + trgm)

```python
async def keyword_search(
    query: str,
    entity_id: str | None = None,
    top_k: int = 20,
) -> List[ChunkResult]:
    sql = """
        SELECT
            c.id,
            c.chunk_text,
            c.source_doc_id,
            c.entity_id,
            c.freshness_score,
            c.trust_score,
            sd.source_url,
            sd.source_type,
            sd.fetched_at,
            ts_rank(to_tsvector('english', c.chunk_text),
                    plainto_tsquery('english', $1)) AS similarity
        FROM chunks c
        JOIN source_documents sd ON sd.id = c.source_doc_id
        WHERE to_tsvector('english', c.chunk_text) @@ plainto_tsquery('english', $1)
          AND ($2::uuid IS NULL OR c.entity_id = $2)
        ORDER BY similarity DESC
        LIMIT $3
    """
    rows = await db.fetch(sql, query, entity_id, top_k)
    return [ChunkResult(**row) for row in rows]
```

---

## Reciprocal Rank Fusion (merge)

```python
def merge_results_rrf(
    vector_results: List[ChunkResult],
    keyword_results: List[ChunkResult],
    k: int = 60,
) -> List[ChunkResult]:
    scores: dict[str, float] = {}
    all_chunks: dict[str, ChunkResult] = {}

    for rank, chunk in enumerate(vector_results):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)
        all_chunks[chunk.id] = chunk

    for rank, chunk in enumerate(keyword_results):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)
        all_chunks[chunk.id] = chunk

    sorted_ids = sorted(scores, key=scores.get, reverse=True)
    return [all_chunks[cid] for cid in sorted_ids]
```

---

## Final Scoring & Ranking

```python
def score_chunk(chunk: ChunkResult, semantic_sim: float) -> float:
    """
    Final ranking score. Tune weights based on use case.
    """
    SOURCE_AUTHORITY = {
        "news_article":     0.9,
        "linkedin":         0.85,
        "company_website":  0.8,
        "crunchbase":       0.8,
        "github":           0.75,
        "blog_post":        0.6,
        "job_board":        0.6,
        "unknown":          0.3,
    }
    authority = SOURCE_AUTHORITY.get(chunk.source_type, 0.3)

    return (
        0.40 * semantic_sim
        + 0.25 * chunk.freshness_score
        + 0.20 * chunk.trust_score
        + 0.15 * authority
    )

def rank_chunks(chunks: List[ChunkResult]) -> List[ChunkResult]:
    for c in chunks:
        c.final_score = score_chunk(c, c.similarity)
    return sorted(chunks, key=lambda c: c.final_score, reverse=True)
```

---

## Freshness Score Calculation

```python
import math
from datetime import datetime, timezone

def compute_freshness(fetched_at: datetime, decay_rate: float = 0.05) -> float:
    """
    Exponential decay. Score = 1.0 when just fetched, approaches 0 over weeks.
    decay_rate=0.05 → ~0.7 after 7 days, ~0.5 after 14 days
    """
    days_old = (datetime.now(timezone.utc) - fetched_at).days
    return max(0.0, math.exp(-decay_rate * days_old))
```

---

## Context Window Assembly

```python
def assemble_context(chunks: List[ChunkResult], max_tokens: int = 3000) -> str:
    """
    Assemble top-ranked chunks into LLM context string.
    Include source metadata for citation.
    """
    context_parts = []
    token_count = 0

    for chunk in chunks:
        snippet = (
            f"[SOURCE: {chunk.source_url} | type={chunk.source_type} "
            f"| fetched={chunk.fetched_at.date()} | trust={chunk.trust_score:.2f}]\n"
            f"{chunk.chunk_text}\n"
        )
        estimated_tokens = len(snippet) // 4
        if token_count + estimated_tokens > max_tokens:
            break
        context_parts.append(snippet)
        token_count += estimated_tokens

    return "\n---\n".join(context_parts)
```

---

## File locations

```
backend/
  services/
    retrieval/
      vector_search.py
      keyword_search.py
      merger.py
      ranker.py
      context_assembler.py
  tests/
    test_retrieval.py
```