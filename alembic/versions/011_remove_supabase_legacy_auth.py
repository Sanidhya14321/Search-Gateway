"""Remove legacy Supabase auth artifacts.

Revision ID: 011
Revises: 010
"""

from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None

USER_TABLES = [
    "user_search_history",
    "user_saved_entities",
    "user_saved_searches",
    "user_enrichment_jobs",
    "user_signal_feed",
    "user_api_keys",
]


def upgrade() -> None:
    for table in USER_TABLES:
        op.execute(f'DROP POLICY IF EXISTS "{table}_user_isolation" ON {table}')
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute('DROP POLICY IF EXISTS "users_self_only" ON users')
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")

    op.execute("UPDATE users SET auth_provider='local' WHERE auth_provider IS NULL OR auth_provider='supabase'")
    op.execute("ALTER TABLE users ALTER COLUMN auth_provider SET DEFAULT 'local'")

    op.execute("DROP INDEX IF EXISTS idx_users_supabase_id")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS supabase_user_id")


def downgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS supabase_user_id UUID")
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_supabase_id ON users (supabase_user_id)")
    op.execute("ALTER TABLE users ALTER COLUMN auth_provider SET DEFAULT 'supabase'")
