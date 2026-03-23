"""Add observability columns to agent_runs
Revision ID: 003
Revises: 002
"""
from alembic import op

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TABLE IF EXISTS agent_runs ADD COLUMN IF NOT EXISTS trace_id VARCHAR(32)")
    op.execute("ALTER TABLE IF EXISTS agent_runs ADD COLUMN IF NOT EXISTS llm_calls_count INTEGER DEFAULT 0")
    op.execute("ALTER TABLE IF EXISTS agent_runs ADD COLUMN IF NOT EXISTS total_chunks_retrieved INTEGER DEFAULT 0")
    op.execute("ALTER TABLE IF EXISTS agent_runs ADD COLUMN IF NOT EXISTS cache_hit BOOLEAN DEFAULT false")
    op.execute("CREATE INDEX IF NOT EXISTS idx_agent_runs_trace ON agent_runs (trace_id)")

def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_agent_runs_trace")
    op.execute("ALTER TABLE IF EXISTS agent_runs DROP COLUMN IF EXISTS cache_hit")
    op.execute("ALTER TABLE IF EXISTS agent_runs DROP COLUMN IF EXISTS total_chunks_retrieved")
    op.execute("ALTER TABLE IF EXISTS agent_runs DROP COLUMN IF EXISTS llm_calls_count")
    op.execute("ALTER TABLE IF EXISTS agent_runs DROP COLUMN IF EXISTS trace_id")
