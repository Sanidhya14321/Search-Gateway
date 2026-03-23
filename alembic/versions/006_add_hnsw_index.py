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
    op.execute(
        """
        DO $$
        DECLARE
            embedding_typmod INTEGER;
        BEGIN
            SELECT a.atttypmod
            INTO embedding_typmod
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = 'chunks'
              AND a.attname = 'embedding'
              AND a.attnum > 0
              AND NOT a.attisdropped;

            IF embedding_typmod IS NULL THEN
                RAISE NOTICE 'Skipping idx_chunks_embedding_hnsw: chunks.embedding column not found';
            ELSIF embedding_typmod <= 0 THEN
                RAISE NOTICE 'Skipping idx_chunks_embedding_hnsw: chunks.embedding has no fixed dimensions';
            ELSE
                EXECUTE '
                    CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
                    ON chunks
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64)
                ';
            END IF;
        END
        $$
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw")
