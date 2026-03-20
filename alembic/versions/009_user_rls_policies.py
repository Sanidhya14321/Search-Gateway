"""Enable RLS on user tables - users see only their own data.

Revision ID: 009
Revises: 008
"""

from alembic import op

revision = "009"
down_revision = "008"
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
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY \"{table}_user_isolation\"
            ON {table}
            USING (
                user_id = (
                    SELECT id FROM users
                    WHERE supabase_user_id = auth.uid()
                )
            )
            """
        )

    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY "users_self_only"
        ON users
        USING (supabase_user_id = auth.uid())
        """
    )


def downgrade() -> None:
    for table in USER_TABLES:
        op.execute(f'DROP POLICY IF EXISTS "{table}_user_isolation" ON {table}')
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute('DROP POLICY IF EXISTS "users_self_only" ON users')
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")
