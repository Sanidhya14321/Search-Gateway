"""Add HNSW index for chunk embeddings.

Revision ID: 006
Revises: 003
"""

from alembic import op

revision = "006"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
        ON chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw")
