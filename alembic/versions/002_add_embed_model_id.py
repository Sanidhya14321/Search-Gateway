"""Add embed model metadata columns to chunks.

Revision ID: 002
Revises: 001
"""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE IF EXISTS chunks
        ADD COLUMN IF NOT EXISTS embed_model_id VARCHAR(64) NOT NULL DEFAULT 'nomic-embed-text'
        """
    )
    op.execute(
        """
        ALTER TABLE IF EXISTS chunks
        ADD COLUMN IF NOT EXISTS embed_model_version VARCHAR(32) DEFAULT '1.0'
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_chunks_model ON chunks (embed_model_id)")

    # Embedding dimensions are model-dependent and tracked via embed_model_id.
    # Keep chunks.embedding as VECTOR (no fixed dimension in schema).


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_chunks_model")
    op.execute("ALTER TABLE IF EXISTS chunks DROP COLUMN IF EXISTS embed_model_version")
    op.execute("ALTER TABLE IF EXISTS chunks DROP COLUMN IF EXISTS embed_model_id")
