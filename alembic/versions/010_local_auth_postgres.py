"""Add local Postgres auth fields.

Revision ID: 010
Revises: 009
"""

from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(32) DEFAULT 'supabase' NOT NULL")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'users'
                  AND column_name = 'supabase_user_id'
            ) THEN
                UPDATE users
                SET auth_provider = CASE
                    WHEN password_hash IS NOT NULL THEN 'local'
                    WHEN supabase_user_id IS NOT NULL THEN 'supabase'
                    ELSE 'local'
                END;
            ELSE
                UPDATE users
                SET auth_provider = CASE
                    WHEN password_hash IS NOT NULL THEN 'local'
                    ELSE 'local'
                END;
            END IF;
        END $$
        """
    )

    # Allow existing table to support non-Supabase local users.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'users'
                  AND column_name = 'supabase_user_id'
            ) THEN
                ALTER TABLE users ALTER COLUMN supabase_user_id DROP NOT NULL;
            END IF;
        END $$
        """
    )


def downgrade() -> None:
    op.execute("UPDATE users SET supabase_user_id = COALESCE(supabase_user_id, id)")
    op.execute("ALTER TABLE users ALTER COLUMN supabase_user_id SET NOT NULL")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS auth_provider")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS password_hash")
