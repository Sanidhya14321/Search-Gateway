"""Initialize baseline schema from SQL bootstrap.

Revision ID: 001
Revises: None
"""

from pathlib import Path

from alembic import op
from sqlalchemy import text

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    companies_exists = bind.execute(text("SELECT to_regclass('public.companies')")).scalar()
    if companies_exists:
        return

    schema_path = Path(__file__).resolve().parents[2] / "supabase" / "migrations" / "001_initial.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    bind.execute(text(schema_sql))


def downgrade() -> None:
    # Baseline schema downgrade is intentionally a no-op.
    pass
