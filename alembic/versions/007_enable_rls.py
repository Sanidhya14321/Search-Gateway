"""Enable row-level security for core tables.

Revision ID: 007
Revises: 006
"""

from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None

TABLES = [
    "companies",
    "people",
    "roles",
    "source_documents",
    "chunks",
    "facts",
    "signals",
    "agent_runs",
    "crawl_queue",
    "query_cache",
]


POLICY_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = '{table_name}'
          AND policyname = 'service_role_full_access'
    ) THEN
        CREATE POLICY service_role_full_access
        ON {table_name}
        FOR ALL
        TO PUBLIC
        USING (current_setting('request.jwt.claim.role', true) = 'service_role')
        WITH CHECK (current_setting('request.jwt.claim.role', true) = 'service_role');
    END IF;
END $$;
"""


DROP_POLICY_SQL = """
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = '{table_name}'
          AND policyname = 'service_role_full_access'
    ) THEN
        DROP POLICY service_role_full_access ON {table_name};
    END IF;
END $$;
"""


def upgrade() -> None:
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(POLICY_SQL.format(table_name=table))


def downgrade() -> None:
    for table in TABLES:
        op.execute(DROP_POLICY_SQL.format(table_name=table))
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
