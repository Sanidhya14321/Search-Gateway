"""Enable RLS on user tables - users see only their own data.

Revision ID: 009
Revises: 008
"""

from alembic import op
from sqlalchemy import text

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
    bind = op.get_bind()
    auth_uid_exists = bind.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.routines
                WHERE routine_schema = 'auth' AND routine_name = 'uid'
            )
            """
        )
    ).scalar()

    if not auth_uid_exists:
        # Non-Supabase Postgres environments do not expose auth.uid().
        return

    for table in USER_TABLES:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF to_regclass('public.{table}') IS NOT NULL THEN
                    EXECUTE 'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY';
                END IF;
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_policies
                    WHERE schemaname = 'public'
                      AND tablename = '{table}'
                      AND policyname = '{table}_user_isolation'
                ) THEN
                    EXECUTE '
                        CREATE POLICY "{table}_user_isolation"
                        ON {table}
                        USING (
                            user_id = (
                                SELECT id FROM users
                                WHERE supabase_user_id = auth.uid()
                            )
                        )
                    ';
                END IF;
            END $$
            """
        )

    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.users') IS NOT NULL THEN
                ALTER TABLE users ENABLE ROW LEVEL SECURITY;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename = 'users'
                  AND policyname = 'users_self_only'
            ) THEN
                CREATE POLICY "users_self_only"
                ON users
                USING (supabase_user_id = auth.uid());
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    for table in USER_TABLES:
        op.execute(f'DROP POLICY IF EXISTS "{table}_user_isolation" ON {table}')
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute('DROP POLICY IF EXISTS "users_self_only" ON users')
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")
