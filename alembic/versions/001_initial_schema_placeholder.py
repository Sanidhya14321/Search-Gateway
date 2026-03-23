"""Initial schema placeholder revision.

Revision ID: 001
Revises: None

This repository currently starts tracked revisions at 002 while base schema
is provisioned separately (SQL/bootstrap scripts). This no-op revision keeps
Alembic's graph consistent for upgrade traversal.
"""

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: baseline schema is created outside this revision chain.
    pass


def downgrade() -> None:
    # No-op counterpart.
    pass
