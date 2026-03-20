# CRMind — AI Search + CRM Intelligence System
## Product Requirements Document & Architecture Guide

---

## 1. Product Overview

**CRMind** is an entity-first, citation-aware, freshness-ranked AI search and CRM intelligence platform. It functions as a Crustdata-style intelligence gateway: given a company, person, or account query, the system resolves the entity, pulls multi-source evidence, deduplicates and ranks results, and returns a structured response with traceable citations.

### 1.1 Problem Statement

Sales, recruiting, and ops teams rely on stale CRM data, manual Google searches, and expensive third-party enrichment APIs. There is no open, auditable, agent-powered system that:
- Resolves entities with confidence scores
- Attaches freshness and trust metadata to every fact
- Exposes agent workflows for enrichment, briefing, and research
- Returns structured, citation-backed JSON rather than freeform LLM answers

### 1.2 Goals

| Goal | Success Metric |
|------|---------------|
| Entity resolution accuracy | >85% canonical match rate on test set |
| Source freshness | <7 days average for active entities |
| Citation coverage | Every response fact has ≥1 source link |
| API response time (cached) | <800ms P95 |
| API response time (live agent) | <8s P95 |
| Free-tier deployment cost | $0/month on Vercel + Supabase free tier |

### 1.3 Non-Goals

- Not a full CRM (no deal/pipeline management)
- Not a real-time scraping service for every request in production
- Not a general-purpose LLM chatbot

---

## 2. User Personas

### P1 — Sales Development Rep (SDR)
Needs account briefs, hiring signals, and recent company changes before outreach.

### P2 — Recruiter
Needs to find senior engineers at a company with verified LinkedIn/GitHub sources.

### P3 — AI Engineer / Builder
Needs an API and agent graph they can embed into their own CRM or workflow tool.

### P4 — Ops / Data Team
Needs to enrich a bulk lead list and write back structured, deduped records.

---

## 3. Core Features

### F1 — Entity Search
- Search by company name, domain, person name, or title
- Returns canonical entity card with confidence score
- Attaches all known source URLs

### F2 — Account Intelligence
- Pull hiring signals, funding, product changes, leadership moves
- Return a sales-relevant brief with timeline and citations

### F3 — Contact Intelligence
- Find and verify people at a company
- Return role, seniority, contact hints, and source evidence

### F4 — CRM Enrichment
- Upload a CSV/JSON lead list
- Enrich each row with verified facts
- Flag missing fields, deduplicate, write back

### F5 — Source-of-Truth Crawling
- Accept a URL or domain
- Crawl, chunk, embed, store, and schedule refresh

### F6 — Agent Workflows
- Lead Finder, Account Brief, Enrichment, Research, Ops/Debug agents
- All agents are tool-using, retrieval-grounded, citation-returning

### F7 — Debugging Panel (local/demo only)
- Show which sources were retrieved
- Show why each result was ranked
- Show pipeline step timings

---

## 4. System Architecture

### 4.1 High-Level Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAYER D: AGENT RESPONSE                  │
│   LangGraph Agent  ──  Tool Calls  ──  Synthesis  ──  Citations │
├─────────────────────────────────────────────────────────────────┤
│                        LAYER C: RETRIEVAL                       │
│   Keyword Search  ──  Vector Search  ──  Freshness Rank         │
├─────────────────────────────────────────────────────────────────┤
│                        LAYER B: NORMALIZATION                   │
│   Entity Resolution  ──  Dedup  ──  Trust Score  ──  JSON       │
├─────────────────────────────────────────────────────────────────┤
│                        LAYER A: INGESTION                       │
│   Web Crawl  ──  PDF Parse  ──  API Feeds  ──  Upload           │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Local (Demo) Stack

| Component | Tool |
|-----------|------|
| Frontend | Next.js 14 (App Router) |
| Backend API | FastAPI |
| Agent Orchestration | LangGraph |
| Database | PostgreSQL 16 |
| Vector Store | pgvector (in Postgres) |
| Embeddings | `nomic-embed-text` via Ollama |
| LLM | `llama3` or `mistral` via Ollama |
| Crawler | Playwright (async) |
| Queue | Redis + ARQ |
| Containerization | Docker Compose |

### 4.3 Deployment (Free-Tier) Stack

| Component | Tool |
|-----------|------|
| Frontend | Vercel Hobby (free) |
| Backend API | Render free tier or Cloudflare Workers |
| Database | Supabase free (Postgres + pgvector + auth) |
| Embeddings | `text-embedding-3-small` via OpenAI (batched) |
| LLM | `claude-haiku` or `gpt-4o-mini` for low cost |
| Crawler | Cloudflare Browser Rendering (limited) |
| Ingestion Jobs | GitHub Actions (scheduled CRON) |
| Caching | Supabase Edge Functions or Vercel Edge Cache |

### 4.4 Local Pipeline Flow

```
Demo Query / UI
      │
      ▼
Agent Router (LangGraph)
      │
      ▼
Entity Resolver ──────────────────────────────┐
      │                                        │
      ▼                                        ▼
Live Web Crawler (Playwright)         Vector Store Lookup (pgvector)
      │                                        │
      ▼                                        │
Extractor + Cleaner                            │
      │                                        │
      ▼                                        │
Chunker (recursive / semantic)                 │
      │                                        │
      ▼                                        │
Embedding Model (Ollama)                       │
      │                                        │
      ▼                                        │
Vector Store (pgvector) ◄──────────────────────┘
      │
      ▼
Retriever + Ranker (freshness × trust × similarity)
      │
      ▼
LLM Synthesizer (Ollama / tool-calling)
      │
      ▼
Structured CRM Response + Citations
      │
      ▼
UI with Source Links + Debug Panel
```

### 4.5 Deployment Pipeline Flow

```
User Query
      │
      ▼
Frontend (Vercel) → Light API Gateway (Cloudflare / Render)
      │
      ▼
Entity Resolver
      │
      ▼
Supabase Postgres + pgvector
      │
      ├─── Cache HIT ──► Cached Retrieval Results
      │
      └─── Cache MISS ──► Small LLM Call (haiku/gpt-4o-mini)
                                │
                                ▼
                    Structured JSON + Citations

[Background CRON via GitHub Actions]
Batch Ingestion → Extract + Clean → Embed + Upsert → Supabase
```

---

## 5. API Design

### 5.1 Core Endpoints

```
POST   /api/v1/search              # Entity search
POST   /api/v1/enrich              # Single entity enrichment
POST   /api/v1/enrich/batch        # Bulk CSV enrichment
GET    /api/v1/entity/{id}         # Get canonical entity card
GET    /api/v1/account/{id}/brief  # Account intelligence brief
GET    /api/v1/contact/{id}        # Contact intelligence profile
POST   /api/v1/crawl               # Trigger crawl for URL/domain
GET    /api/v1/signals/{entity_id} # Get signals for entity
POST   /api/v1/agent/run           # Run a named agent workflow
GET    /api/v1/sources/{entity_id} # All sources for an entity
GET    /api/v1/health              # Health + pipeline status
```

### 5.2 Canonical Response Shape

```json
{
  "entity_id": "comp_abc123",
  "entity_type": "company",
  "canonical_name": "Acme Corp",
  "confidence": 0.94,
  "summary": "Acme Corp is a Series B SaaS company...",
  "facts": [
    {
      "fact_id": "fact_001",
      "claim": "Acme Corp raised $12M Series B in March 2024",
      "confidence": 0.91,
      "freshness_score": 0.88,
      "trust_score": 0.85,
      "sources": [
        {
          "source_id": "src_xyz",
          "url": "https://techcrunch.com/...",
          "source_type": "news",
          "fetched_at": "2024-03-15T10:22:00Z",
          "excerpt": "Acme Corp announced..."
        }
      ]
    }
  ],
  "signals": [
    {
      "signal_type": "hiring",
      "description": "Posted 4 senior engineering roles in past 30 days",
      "confidence": 0.87,
      "source_url": "https://acme.com/careers"
    }
  ],
  "people": [...],
  "retrieved_at": "2024-04-01T09:00:00Z",
  "pipeline_version": "1.2.0"
}
```

---

## 6. Ranking & Scoring Model

Every retrieved chunk is scored before synthesis:

```
final_score = (
  0.40 × semantic_similarity
  + 0.25 × freshness_score
  + 0.20 × trust_score
  + 0.15 × source_authority
)

freshness_score = exp(-λ × days_since_fetched)   # λ = 0.05
trust_score     = f(source_type, domain_authority, cross_reference_count)
source_authority = normalized domain ranking (news > LinkedIn > blog > unknown)
```

---

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| API Uptime | 99.5% (deployment) |
| Data freshness SLA | Active entities refreshed every 7 days |
| Crawl rate limiting | Max 1 req/3s per domain |
| PII handling | No storage of personal emails without consent flag |
| Audit log | Every agent invocation logged with input/output hash |
| Rate limiting | 100 req/min per API key |

---

## 8. Security Considerations

- All API keys stored in environment variables, never in code
- Supabase Row Level Security (RLS) enabled on all tables
- Crawl robots.txt respected by default; override flag for private use
- Input sanitization on all search/enrich endpoints
- JWT-based auth for multi-user deployment

---

## 9. Observability

- Structured JSON logging (loguru in FastAPI)
- Each pipeline step emits: `step_name`, `duration_ms`, `entity_id`, `success`
- LangGraph traces stored in `agent_runs` table
- Sentry for error tracking (free tier)
- Simple `/health` endpoint reports DB connectivity, queue depth, last crawl time