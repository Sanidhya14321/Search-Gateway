"""Add user auth and interaction storage tables.

Revision ID: 008
Revises: 007
"""

from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          supabase_user_id UUID UNIQUE NOT NULL,
          email VARCHAR(512) UNIQUE NOT NULL,
          display_name VARCHAR(255),
          avatar_url VARCHAR(1024),
          plan VARCHAR(32) DEFAULT 'free',
          is_active BOOLEAN DEFAULT TRUE,
          preferences JSONB DEFAULT '{}',
          created_at TIMESTAMPTZ DEFAULT NOW(),
          updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_supabase_id ON users (supabase_user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_api_keys (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          key_hash VARCHAR(256) NOT NULL,
          key_prefix VARCHAR(16) NOT NULL,
          name VARCHAR(255) NOT NULL,
          last_used_at TIMESTAMPTZ,
          expires_at TIMESTAMPTZ,
          is_active BOOLEAN DEFAULT TRUE,
          created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user ON user_api_keys (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON user_api_keys (key_prefix)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_search_history (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          query TEXT NOT NULL,
          workflow_name VARCHAR(128),
          entity_id UUID,
          entity_type VARCHAR(32),
          entity_name VARCHAR(512),
          result_count INT DEFAULT 0,
          agent_run_id UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
          created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_search_history_user ON user_search_history (user_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_search_history_entity ON user_search_history (entity_id)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_saved_entities (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          entity_id UUID NOT NULL,
          entity_type entity_type NOT NULL,
          entity_name VARCHAR(512) NOT NULL,
          note TEXT,
          tags TEXT[] DEFAULT '{}',
          created_at TIMESTAMPTZ DEFAULT NOW(),
          UNIQUE (user_id, entity_id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_saved_entities_user ON user_saved_entities (user_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_saved_entities_tags ON user_saved_entities USING gin (tags)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_saved_searches (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          name VARCHAR(255) NOT NULL,
          query TEXT NOT NULL,
          workflow_name VARCHAR(128),
          filters JSONB DEFAULT '{}',
          alert_enabled BOOLEAN DEFAULT FALSE,
          last_run_at TIMESTAMPTZ,
          run_count INT DEFAULT 0,
          created_at TIMESTAMPTZ DEFAULT NOW(),
          updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_saved_searches_user ON user_saved_searches (user_id, created_at DESC)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_enrichment_jobs (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          job_name VARCHAR(255),
          agent_run_id UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
          status VARCHAR(32) DEFAULT 'pending',
          input_row_count INT DEFAULT 0,
          output_row_count INT DEFAULT 0,
          flagged_count INT DEFAULT 0,
          error_message TEXT,
          input_file_url VARCHAR(1024),
          output_data JSONB,
          created_at TIMESTAMPTZ DEFAULT NOW(),
          completed_at TIMESTAMPTZ
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_user ON user_enrichment_jobs (user_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_status ON user_enrichment_jobs (status)")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_signal_feed (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          signal_id UUID NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
          is_read BOOLEAN DEFAULT FALSE,
          is_dismissed BOOLEAN DEFAULT FALSE,
          created_at TIMESTAMPTZ DEFAULT NOW(),
          UNIQUE (user_id, signal_id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_signal_feed_user ON user_signal_feed (user_id, is_read, created_at DESC)")

    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_users_updated_at'
          ) THEN
            CREATE TRIGGER trg_users_updated_at
              BEFORE UPDATE ON users
              FOR EACH ROW EXECUTE FUNCTION update_updated_at();
          END IF;
        END $$
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_trigger WHERE tgname = 'trg_saved_searches_updated_at'
          ) THEN
            CREATE TRIGGER trg_saved_searches_updated_at
              BEFORE UPDATE ON user_saved_searches
              FOR EACH ROW EXECUTE FUNCTION update_updated_at();
          END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_saved_searches_updated_at ON user_saved_searches")
    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users")

    op.execute("DROP TABLE IF EXISTS user_signal_feed")
    op.execute("DROP TABLE IF EXISTS user_enrichment_jobs")
    op.execute("DROP TABLE IF EXISTS user_saved_searches")
    op.execute("DROP TABLE IF EXISTS user_saved_entities")
    op.execute("DROP TABLE IF EXISTS user_search_history")
    op.execute("DROP TABLE IF EXISTS user_api_keys")
    op.execute("DROP TABLE IF EXISTS users")
