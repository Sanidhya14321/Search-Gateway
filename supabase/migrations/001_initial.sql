-- ============================================================
-- CRMind — Canonical Database Schema
-- PostgreSQL 16 + pgvector extension
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- for fuzzy text search

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE entity_type AS ENUM (
  'company', 'person', 'account', 'role'
);

CREATE TYPE source_type AS ENUM (
  'company_website', 'news_article', 'linkedin', 'github',
  'job_board', 'crunchbase', 'twitter', 'blog_post',
  'pdf_upload', 'api_feed', 'unknown'
);

CREATE TYPE signal_type AS ENUM (
  'hiring', 'funding', 'leadership_change', 'product_launch',
  'website_change', 'expansion', 'layoff', 'partnership',
  'acquisition', 'ipo', 'other'
);

CREATE TYPE crawl_status AS ENUM (
  'pending', 'in_progress', 'completed', 'failed', 'skipped'
);

CREATE TYPE agent_status AS ENUM (
  'running', 'completed', 'failed', 'cancelled'
);

CREATE TYPE seniority_level AS ENUM (
  'intern', 'junior', 'mid', 'senior', 'staff', 'principal',
  'director', 'vp', 'c_level', 'founder', 'unknown'
);

-- ============================================================
-- CORE ENTITY TABLES
-- ============================================================

-- Companies
CREATE TABLE companies (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  canonical_id      VARCHAR(64) UNIQUE NOT NULL,        -- e.g. "comp_acmecorp"
  canonical_name    VARCHAR(512) NOT NULL,
  domain            VARCHAR(255),
  description       TEXT,
  industry          VARCHAR(255),
  hq_location       VARCHAR(255),
  employee_count    INT,
  founded_year      INT,
  linkedin_url      VARCHAR(1024),
  crunchbase_url    VARCHAR(1024),
  logo_url          VARCHAR(1024),
  aliases           TEXT[],                             -- alternate names/spellings
  trust_score       FLOAT DEFAULT 0.5,
  freshness_score   FLOAT DEFAULT 0.5,
  is_verified       BOOLEAN DEFAULT FALSE,
  metadata          JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_companies_domain ON companies (domain);
CREATE INDEX idx_companies_canonical_name ON companies USING gin (canonical_name gin_trgm_ops);
CREATE INDEX idx_companies_aliases ON companies USING gin (aliases);

-- People
CREATE TABLE people (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  canonical_id      VARCHAR(64) UNIQUE NOT NULL,        -- e.g. "per_johndoe_acme"
  full_name         VARCHAR(512) NOT NULL,
  first_name        VARCHAR(255),
  last_name         VARCHAR(255),
  current_title     VARCHAR(512),
  seniority_level   seniority_level DEFAULT 'unknown',
  current_company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
  email_hint        VARCHAR(512),                       -- "j***@acme.com" pattern
  linkedin_url      VARCHAR(1024),
  github_url        VARCHAR(1024),
  twitter_url       VARCHAR(1024),
  location          VARCHAR(255),
  bio               TEXT,
  skills            TEXT[],
  trust_score       FLOAT DEFAULT 0.5,
  freshness_score   FLOAT DEFAULT 0.5,
  is_verified       BOOLEAN DEFAULT FALSE,
  metadata          JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_people_company ON people (current_company_id);
CREATE INDEX idx_people_name ON people USING gin (full_name gin_trgm_ops);
CREATE INDEX idx_people_title ON people USING gin (current_title gin_trgm_ops);
CREATE INDEX idx_people_seniority ON people (seniority_level);

-- Roles / Employment History
CREATE TABLE roles (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  person_id       UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  company_id      UUID REFERENCES companies(id) ON DELETE SET NULL,
  title           VARCHAR(512) NOT NULL,
  seniority_level seniority_level DEFAULT 'unknown',
  department      VARCHAR(255),
  start_date      DATE,
  end_date        DATE,
  is_current      BOOLEAN DEFAULT FALSE,
  source_url      VARCHAR(1024),
  confidence      FLOAT DEFAULT 0.5,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_roles_person ON roles (person_id);
CREATE INDEX idx_roles_company ON roles (company_id);
CREATE INDEX idx_roles_current ON roles (is_current) WHERE is_current = TRUE;

-- Accounts (CRM-level grouping, can span multiple companies)
CREATE TABLE accounts (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  canonical_id    VARCHAR(64) UNIQUE NOT NULL,
  name            VARCHAR(512) NOT NULL,
  owner_email     VARCHAR(512),
  stage           VARCHAR(128),
  notes           TEXT,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Account → Company mapping
CREATE TABLE account_companies (
  account_id  UUID REFERENCES accounts(id) ON DELETE CASCADE,
  company_id  UUID REFERENCES companies(id) ON DELETE CASCADE,
  PRIMARY KEY (account_id, company_id)
);

-- Account → Person mapping
CREATE TABLE account_contacts (
  account_id  UUID REFERENCES accounts(id) ON DELETE CASCADE,
  person_id   UUID REFERENCES people(id) ON DELETE CASCADE,
  role_label  VARCHAR(255),   -- e.g. "champion", "decision maker"
  PRIMARY KEY (account_id, person_id)
);

-- ============================================================
-- INGESTION & SOURCE TABLES
-- ============================================================

-- Source Documents (raw crawled/ingested pages)
CREATE TABLE source_documents (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_url      VARCHAR(2048) NOT NULL,
  source_type     source_type DEFAULT 'unknown',
  domain          VARCHAR(255),
  title           TEXT,
  raw_html        TEXT,
  clean_text      TEXT,
  language        VARCHAR(16) DEFAULT 'en',
  entity_id       UUID,                                 -- nullable: linked entity
  entity_type     entity_type,
  fetched_at      TIMESTAMPTZ DEFAULT NOW(),
  last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
  content_hash    VARCHAR(64),                          -- SHA-256 for change detection
  trust_score     FLOAT DEFAULT 0.5,
  freshness_score FLOAT DEFAULT 0.5,
  crawl_status    crawl_status DEFAULT 'completed',
  http_status     INT,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sources_url ON source_documents (source_url);
CREATE INDEX idx_sources_entity ON source_documents (entity_id, entity_type);
CREATE INDEX idx_sources_domain ON source_documents (domain);
CREATE INDEX idx_sources_fetched ON source_documents (fetched_at DESC);

-- Crawl Queue
CREATE TABLE crawl_queue (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  url             VARCHAR(2048) NOT NULL,
  domain          VARCHAR(255),
  entity_id       UUID,
  entity_type     entity_type,
  priority        INT DEFAULT 5,                        -- 1 = highest
  status          crawl_status DEFAULT 'pending',
  attempts        INT DEFAULT 0,
  max_attempts    INT DEFAULT 3,
  scheduled_at    TIMESTAMPTZ DEFAULT NOW(),
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ,
  error_message   TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_crawl_queue_status ON crawl_queue (status, scheduled_at)
  WHERE status IN ('pending', 'failed');

-- ============================================================
-- CHUNKS & VECTOR EMBEDDINGS
-- ============================================================

-- Chunks (text segments from source documents)
CREATE TABLE chunks (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_doc_id   UUID NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
  chunk_index     INT NOT NULL,
  chunk_text      TEXT NOT NULL,
  char_start      INT,
  char_end        INT,
  token_count     INT,
  entity_id       UUID,
  entity_type     entity_type,
  freshness_score FLOAT DEFAULT 0.5,
  trust_score     FLOAT DEFAULT 0.5,
  embedding       VECTOR,
  embed_model_id      VARCHAR(64)  NOT NULL DEFAULT 'nomic-embed-text',
  embed_model_version VARCHAR(32)  DEFAULT '1.0',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chunks_source ON chunks (source_doc_id);
CREATE INDEX idx_chunks_entity ON chunks (entity_id, entity_type);
CREATE INDEX idx_chunks_model ON chunks (embed_model_id);
-- HNSW requires fixed dimensions. Create this index in a later migration
-- after embedding model/dimension are finalized for the environment.

-- ============================================================
-- FACTS & SIGNALS
-- ============================================================

-- Extracted Facts (claims derived from sources)
CREATE TABLE facts (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_id       UUID NOT NULL,
  entity_type     entity_type NOT NULL,
  claim           TEXT NOT NULL,
  fact_category   VARCHAR(128),                         -- "funding", "headcount", etc.
  confidence      FLOAT DEFAULT 0.5,
  trust_score     FLOAT DEFAULT 0.5,
  freshness_score FLOAT DEFAULT 0.5,
  source_doc_id   UUID REFERENCES source_documents(id) ON DELETE SET NULL,
  chunk_id        UUID REFERENCES chunks(id) ON DELETE SET NULL,
  source_url      VARCHAR(2048),
  extracted_at    TIMESTAMPTZ DEFAULT NOW(),
  valid_from      DATE,
  valid_until     DATE,
  is_superseded   BOOLEAN DEFAULT FALSE,
  superseded_by   UUID REFERENCES facts(id),
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_facts_entity ON facts (entity_id, entity_type);
CREATE INDEX idx_facts_category ON facts (fact_category);
CREATE INDEX idx_facts_confidence ON facts (confidence DESC);

-- Signals (derived, sales-relevant events)
CREATE TABLE signals (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_id       UUID NOT NULL,
  entity_type     entity_type NOT NULL,
  signal_type     signal_type NOT NULL,
  description     TEXT NOT NULL,
  confidence      FLOAT DEFAULT 0.5,
  impact_score    FLOAT DEFAULT 0.5,                   -- how sales-relevant
  source_url      VARCHAR(2048),
  source_doc_id   UUID REFERENCES source_documents(id) ON DELETE SET NULL,
  detected_at     TIMESTAMPTZ DEFAULT NOW(),
  event_date      DATE,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signals_entity ON signals (entity_id, entity_type);
CREATE INDEX idx_signals_type ON signals (signal_type);
CREATE INDEX idx_signals_detected ON signals (detected_at DESC);

-- ============================================================
-- AGENT & PIPELINE TRACKING
-- ============================================================

-- Agent Runs (every LangGraph invocation)
CREATE TABLE agent_runs (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  run_id          VARCHAR(128) UNIQUE NOT NULL,
  workflow_name   VARCHAR(128) NOT NULL,               -- e.g. "lead_finder"
  status          agent_status DEFAULT 'running',
  input_payload   JSONB NOT NULL,
  output_payload  JSONB,
  input_hash      VARCHAR(64),                         -- SHA-256 for dedup
  steps_log       JSONB DEFAULT '[]',                  -- array of step traces
  tool_calls      JSONB DEFAULT '[]',                  -- list of tool invocations
  trace_id                VARCHAR(32),
  llm_calls_count         INT DEFAULT 0,
  total_chunks_retrieved  INT DEFAULT 0,
  cache_hit               BOOLEAN DEFAULT FALSE,
  tokens_used     INT DEFAULT 0,
  duration_ms     INT,
  error_message   TEXT,
  user_id         VARCHAR(255),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  completed_at    TIMESTAMPTZ
);

CREATE INDEX idx_agent_runs_workflow ON agent_runs (workflow_name, created_at DESC);
CREATE INDEX idx_agent_runs_status ON agent_runs (status);
CREATE INDEX idx_agent_runs_input_hash ON agent_runs (input_hash);

-- Pipeline Step Logs
CREATE TABLE pipeline_logs (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_run_id    UUID REFERENCES agent_runs(id) ON DELETE CASCADE,
  step_name       VARCHAR(128) NOT NULL,
  step_index      INT,
  status          VARCHAR(32),
  duration_ms     INT,
  input_summary   TEXT,
  output_summary  TEXT,
  error_message   TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pipeline_logs_run ON pipeline_logs (agent_run_id);

-- ============================================================
-- CACHING
-- ============================================================

-- Query Result Cache (avoid redundant agent runs)
CREATE TABLE query_cache (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  query_hash      VARCHAR(64) UNIQUE NOT NULL,
  query_text      TEXT NOT NULL,
  workflow_name   VARCHAR(128),
  response_json   JSONB NOT NULL,
  hit_count       INT DEFAULT 1,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  expires_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_query_cache_hash ON query_cache (query_hash);
CREATE INDEX idx_query_cache_expires ON query_cache (expires_at);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- Enriched person view with current company
CREATE VIEW v_people_enriched AS
SELECT
  p.*,
  c.canonical_name   AS company_name,
  c.domain           AS company_domain,
  c.industry         AS company_industry,
  r.title            AS verified_title,
  r.department       AS department
FROM people p
LEFT JOIN companies c ON p.current_company_id = c.id
LEFT JOIN roles r ON r.person_id = p.id AND r.is_current = TRUE;

-- Active signals with entity names
CREATE VIEW v_signals_with_entity AS
SELECT
  s.*,
  CASE
    WHEN s.entity_type = 'company' THEN c.canonical_name
    WHEN s.entity_type = 'person'  THEN pe.full_name
    ELSE 'Unknown'
  END AS entity_name
FROM signals s
LEFT JOIN companies c  ON s.entity_type = 'company' AND s.entity_id = c.id
LEFT JOIN people    pe ON s.entity_type = 'person'  AND s.entity_id = pe.id
ORDER BY s.detected_at DESC;

-- Stale entity candidates (needs refresh)
CREATE VIEW v_stale_entities AS
SELECT
  'company'::TEXT AS entity_type,
  id,
  canonical_name AS name,
  updated_at,
  freshness_score
FROM companies
WHERE freshness_score < 0.4 OR updated_at < NOW() - INTERVAL '7 days'
UNION ALL
SELECT
  'person'::TEXT,
  id,
  full_name,
  updated_at,
  freshness_score
FROM people
WHERE freshness_score < 0.4 OR updated_at < NOW() - INTERVAL '7 days'
ORDER BY freshness_score ASC;

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Auto-update updated_at on row changes
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_companies_updated_at
  BEFORE UPDATE ON companies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_people_updated_at
  BEFORE UPDATE ON people
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_accounts_updated_at
  BEFORE UPDATE ON accounts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Compute freshness score from fetched_at age
CREATE OR REPLACE FUNCTION compute_freshness(fetched_at TIMESTAMPTZ)
RETURNS FLOAT AS $$
DECLARE
  days_old FLOAT;
BEGIN
  days_old := EXTRACT(EPOCH FROM (NOW() - fetched_at)) / 86400.0;
  RETURN GREATEST(0.0, EXP(-0.05 * days_old));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================
-- USER ACCOUNTS AND INTERACTION STORAGE
-- ============================================================

CREATE TABLE users (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  supabase_user_id    UUID UNIQUE NOT NULL,
  email               VARCHAR(512) UNIQUE NOT NULL,
  display_name        VARCHAR(255),
  avatar_url          VARCHAR(1024),
  plan                VARCHAR(32) DEFAULT 'free',
  is_active           BOOLEAN DEFAULT TRUE,
  preferences         JSONB DEFAULT '{}',
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_supabase_id ON users (supabase_user_id);
CREATE INDEX idx_users_email ON users (email);

CREATE TABLE user_api_keys (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  key_hash        VARCHAR(256) NOT NULL,
  key_prefix      VARCHAR(16) NOT NULL,
  name            VARCHAR(255) NOT NULL,
  last_used_at    TIMESTAMPTZ,
  expires_at      TIMESTAMPTZ,
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user ON user_api_keys (user_id);
CREATE INDEX idx_api_keys_prefix ON user_api_keys (key_prefix);

CREATE TABLE user_search_history (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  query           TEXT NOT NULL,
  workflow_name   VARCHAR(128),
  entity_id       UUID,
  entity_type     VARCHAR(32),
  entity_name     VARCHAR(512),
  result_count    INT DEFAULT 0,
  agent_run_id    UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_search_history_user ON user_search_history (user_id, created_at DESC);
CREATE INDEX idx_search_history_entity ON user_search_history (entity_id);

CREATE TABLE user_saved_entities (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  entity_id       UUID NOT NULL,
  entity_type     entity_type NOT NULL,
  entity_name     VARCHAR(512) NOT NULL,
  note            TEXT,
  tags            TEXT[] DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, entity_id)
);

CREATE INDEX idx_saved_entities_user ON user_saved_entities (user_id, created_at DESC);
CREATE INDEX idx_saved_entities_tags ON user_saved_entities USING gin (tags);

CREATE TABLE user_saved_searches (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  query           TEXT NOT NULL,
  workflow_name   VARCHAR(128),
  filters         JSONB DEFAULT '{}',
  alert_enabled   BOOLEAN DEFAULT FALSE,
  last_run_at     TIMESTAMPTZ,
  run_count       INT DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_saved_searches_user ON user_saved_searches (user_id, created_at DESC);

CREATE TABLE user_enrichment_jobs (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_name         VARCHAR(255),
  agent_run_id     UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
  status           VARCHAR(32) DEFAULT 'pending',
  input_row_count  INT DEFAULT 0,
  output_row_count INT DEFAULT 0,
  flagged_count    INT DEFAULT 0,
  error_message    TEXT,
  input_file_url   VARCHAR(1024),
  output_data      JSONB,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  completed_at     TIMESTAMPTZ
);

CREATE INDEX idx_enrichment_jobs_user ON user_enrichment_jobs (user_id, created_at DESC);
CREATE INDEX idx_enrichment_jobs_status ON user_enrichment_jobs (status);

CREATE TABLE user_signal_feed (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  signal_id       UUID NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
  is_read         BOOLEAN DEFAULT FALSE,
  is_dismissed    BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, signal_id)
);

CREATE INDEX idx_signal_feed_user ON user_signal_feed (user_id, is_read, created_at DESC);

CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_saved_searches_updated_at
  BEFORE UPDATE ON user_saved_searches
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- SEED DATA (for local dev)
-- ============================================================

-- Example company
INSERT INTO companies (canonical_id, canonical_name, domain, industry, trust_score, freshness_score)
VALUES ('comp_example_inc', 'Example Inc', 'example.com', 'SaaS', 0.9, 0.95);