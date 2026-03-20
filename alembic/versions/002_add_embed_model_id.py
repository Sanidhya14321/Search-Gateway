"""Add embed model metadata columns to chunks.

Revision ID: 002
Revises: 001
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "chunks",
        sa.Column(
            "embed_model_id",
            sa.String(length=64),
            nullable=False,
            server_default="nomic-embed-text",
        ),
    )
    op.add_column(
        "chunks",
        sa.Column(
            "embed_model_version",
            sa.String(length=32),
            nullable=True,
            server_default="1.0",
        ),
    )
    op.create_index("idx_chunks_model", "chunks", ["embed_model_id"])

    # Embedding dimensions are model-dependent and tracked via embed_model_id.
    # Keep chunks.embedding as VECTOR (no fixed dimension in schema).


def downgrade():
    op.drop_index("idx_chunks_model", table_name="chunks")
    op.drop_column("chunks", "embed_model_version")
    op.drop_column("chunks", "embed_model_id")
