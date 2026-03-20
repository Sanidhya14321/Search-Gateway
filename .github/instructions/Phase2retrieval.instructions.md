---
description: Load when working on the crawler, chunker, embedding service, vector store, pgvector queries, retrieval pipeline, ranking, or any Phase 2 ingestion and retrieval tasks.
applyTo: "{backend/crawler/**,backend/services/retrieval/**,backend/services/embedding_service.py,backend/scoring/**,backend/routers/crawl.py,tests/test_phase2.py}"
---

# Phase 2 — Retrieval: Crawling, Chunking, Embeddings, Vector Search

## Goal
Full ingestion pipeline, vector store populated, and hybrid ranked retrieval
working end-to-end. After this phase: crawl a URL → chunk → embed → retrieve.

## Checklist
- [ ] 2.1 Web crawler (httpx, static pages only)
- [ ] 2.2 Robots.txt checker + domain rate limiter
- [ ] 2.3 Chunker (RecursiveCharacterTextSplitter)
- [ ] 2.4 Embedding service (OpenAI only)
- [ ] 2.5 Store source document + chunks
- [ ] 2.6 Crawl queue worker (async background)
- [ ] 2.7 Vector search (pgvector cosine)
- [ ] 2.8 Keyword search (Postgres full-text)
- [ ] 2.9 RRF merger + ranker
- [ ] 2.10 Scoring services (freshness, trust, authority)
- [ ] 2.11 POST /api/v1/crawl endpoint
- [ ] 2.12 Phase 2 tests passing

## Step-by-Step Copilot Prompts

### 2.1 — Web crawler (httpx)
```
#file:.agents/skills/web-crawler/SKILL.md
@workspace Implement backend/crawler/fetcher.py with:
- FetchedPage dataclass: url, status, raw_html, clean_text, final_url, error, blocked_by_robots
- _fetch_with_httpx(url, timeout_ms) async — User-Agent: "CRMindBot/1.0"
- fetch_page(url, use_browser=False, respect_robots=True, timeout_ms=15000) dispatcher
  Returns FetchedPage with status=403 if robots blocked
Implement backend/crawler/extractor.py with:
- extract_clean_text(raw_html) — strip script/style/nav/footer/header tags,
  collapse whitespace, return clean plaintext
```

### 2.2 — Robots.txt + rate limiter
```
#file:.agents/skills/web-crawler/SKILL.md
@workspace Implement backend/crawler/robots.py:
- get_robots_parser(domain) with @lru_cache(maxsize=512) — reads /robots.txt
- is_allowed(url, user_agent="CRMindBot") → bool
  Return True if robots.txt is unreachable (fail open)

Implement backend/crawler/rate_limiter.py:
- _last_request_time: dict[str, float] per domain
- _domain_locks: dict[str, asyncio.Lock] per domain
- rate_limited_fetch(url, min_delay=3.0, **kwargs) — enforce delay, then call fetch_page
```

### 2.3 — Chunker
```
#file:.agents/skills/web-crawler/SKILL.md
@workspace Implement backend/crawler/chunker.py:
- chunk_text(text, chunk_size=512, chunk_overlap=64) → List[str]
  Use langchain RecursiveCharacterTextSplitter with separators ["\n\n","\n",". "," ",""]
- estimate_token_count(text) → int  (len(text) // 4)
- chunk_with_metadata(text, source_url, entity_id) → List[dict]
  Each dict: {chunk_text, chunk_index, char_start, char_end, token_count}
```

### 2.4 — Embedding service
```
@workspace Implement backend/services/embedding_service.py:
class EmbeddingService:
  - __init__(model, dimensions)
  - async embed(text: str) → List[float]
    - openai: client.embeddings.create(model=model, input=[text])
  - async embed_batch(texts: List[str], batch_size=100) → List[List[float]]
    Split into batches of batch_size, call embed() per batch, flatten
  Model is read from settings.embedding_model.
```

### 2.5 — Store source documents and chunks
```
@workspace Implement backend/crawler/store.py:
- compute_content_hash(text: str) → str  (SHA-256 hex)
- async store_source_document(db, fetched, clean_text, content_hash, entity_info) → UUID
  INSERT INTO source_documents. Return new doc id.
- async embed_and_store_chunks(db, embed_service, doc_id, chunks, entity_info)
  For each chunk dict from chunk_with_metadata():
    1. embed the chunk_text
    2. INSERT INTO chunks with embedding as pgvector type
  Use executemany for batch inserts where possible.
```

### 2.6 — Crawl queue worker
```
#file:.agents/skills/web-crawler/SKILL.md
@workspace Implement backend/crawler/queue_worker.py:
- async crawl_worker(db_pool, embed_service, batch_size=10)
  Loop: SELECT pending items FOR UPDATE SKIP LOCKED, process each, sleep 10s if empty
- async process_crawl_item(item, db, embed_service)
  1. Mark status=in_progress
  2. rate_limited_fetch(item.url)
  3. extract_clean_text()
  4. compute_content_hash()
  5. If hash unchanged: update last_seen_at only, skip embed
  6. Else: store_source_document() → chunk → embed_and_store_chunks()
  7. Mark status=completed
  8. On error: increment attempts, exponential backoff schedule,
     set status=failed if attempts >= max_attempts
```

### 2.7 — Vector search
```
#file:.agents/skills/rag-retrieval-pipeline/SKILL.md
@workspace Implement backend/services/retrieval/vector_search.py:
- ChunkResult dataclass with all fields: id, chunk_text, source_doc_id, entity_id,
  freshness_score, trust_score, source_url, source_type, fetched_at, similarity, final_score
- async vector_search(query, entity_id=None, entity_type=None, top_k=20, min_similarity=0.3)
  Use pgvector <=> cosine distance operator
  JOIN chunks with source_documents for metadata
  WHERE 1 - (embedding <=> $1) > min_similarity
  Filter by entity_id and entity_type when provided
  Return List[ChunkResult]
```

### 2.8 — Keyword search
```
#file:.agents/skills/rag-retrieval-pipeline/SKILL.md
@workspace Implement backend/services/retrieval/keyword_search.py:
- async keyword_search(query, entity_id=None, top_k=20)
  Use to_tsvector('english', chunk_text) @@ plainto_tsquery('english', $1)
  ts_rank() as similarity score
  JOIN source_documents for metadata
  Return List[ChunkResult]
```

### 2.9 — Merger and ranker
```
#file:.agents/skills/rag-retrieval-pipeline/SKILL.md
@workspace Implement:
backend/services/retrieval/merger.py:
- merge_results_rrf(vector_results, keyword_results, k=60) → List[ChunkResult]
  Reciprocal Rank Fusion: score += 1/(k + rank) for each list
  Deduplicate by chunk id, keep highest total RRF score

backend/services/retrieval/ranker.py:
- score_chunk(chunk, semantic_sim) → float
  formula: 0.4*sim + 0.25*freshness + 0.2*trust + 0.15*authority
- rank_chunks(chunks) → List[ChunkResult] sorted by final_score DESC

backend/services/retrieval/context_assembler.py:
- assemble_context(chunks, max_tokens=3000) → str
  Format: [SOURCE: url | type=X | fetched=date | trust=0.8]\nchunk_text\n---
  Stop when estimated token budget exceeded
```

### 2.10 — Scoring services
```
#file:.agents/skills/trust-freshness-scoring/SKILL.md
@workspace Implement:
backend/scoring/freshness.py — compute_freshness_score(fetched_at, decay_rate=0.05),
  compute_freshness_for_source(fetched_at, source_type), DECAY_RATES dict

backend/scoring/trust.py — compute_trust_score(source_type, cross_ref_count=0, is_verified=False),
  BASE_TRUST dict

backend/scoring/authority.py — compute_source_authority(domain, source_type),
  HIGH_AUTHORITY_DOMAINS dict, SOURCE_TYPE_AUTHORITY dict

backend/scoring/batch_refresh.py — async refresh_entity_scores(entity_id, entity_type, db),
  async batch_refresh_stale_scores(db, threshold_days=7)
```

### 2.11 — Crawl endpoint
```
@workspace Implement backend/routers/crawl.py:
POST /api/v1/crawl
  Request body: {url: str, entity_id: str|None, entity_type: str|None,
                 use_browser: bool = False, priority: int = 5}
  1. Validate URL format
  2. Check is_allowed(url) — return 403 if blocked
  3. INSERT into crawl_queue
  4. Return {status:"queued", crawl_id: UUID, url: str, estimated_position: int}
  Auth required (verify_api_key dependency)
```

### 2.12 — Phase 2 tests
```
@workspace Create tests/test_phase2.py:
- test_extract_clean_text: HTML with nav/script → only body text remains
- test_chunk_text: 2000-char text → multiple chunks, each ≤ 512 chars, overlap present
- test_content_hash_consistency: same text → same hash, different text → different hash
- test_vector_search: seed 3 chunks with embeddings, query matches one, assert top result
- test_keyword_search: same setup, keyword query
- test_merge_rrf: two ranked lists with overlapping items → correct merged order
- test_rank_chunks: chunk with higher freshness+trust ranks above lower-scored chunk
- test_compute_freshness_today: fetched_at=now → score ≥ 0.99
- test_compute_freshness_30_days: fetched_at=30 days ago → score < 0.5
- test_crawl_endpoint_robots_blocked: mock is_allowed=False → 403
Use real test Postgres with pgvector. Use mock EmbeddingService returning fixed vectors.
```

## Key Constraints for This Phase

- The HNSW index (`CREATE INDEX ... USING hnsw`) must exist before doing ANN queries
- Always store embeddings as `VECTOR(768)` — match `settings.embedding_dimensions`
- `content_hash` check prevents re-embedding unchanged pages — never skip this check
- Crawl rate limiter uses per-domain asyncio locks — one lock per domain, never a global lock
- `embed_batch` must chunk into groups of 100 — OpenAI has token limits per batch call
- RRF `k=60` is the standard default — do not change without benchmarking

## Definition of Done

Crawl `https://example.com` → document stored in `source_documents` →
chunks in `chunks` table with embeddings → `vector_search("example company")` returns that chunk in top 3.
`pytest tests/test_phase2.py` passes.