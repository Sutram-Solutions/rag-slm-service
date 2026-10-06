"""baseline chunks table with hnsw index

Revision ID: 5809ccaf2b69
Revises:
Create Date: 2026-10-05 15:38:59.538719

"""

from collections.abc import Sequence

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5809ccaf2b69"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "chunks",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.Text(), nullable=False),
        sa.Column("collection", sa.Text(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        # content is returned to the user; contextualized is what gets embedded
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("contextualized", sa.Text(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("section", sa.Text(), nullable=True),
        sa.Column("language", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(1024), nullable=True),
        sa.Column("embedding_model", sa.Text(), nullable=False),
        sa.Column("embedding_dim", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_chunks_document_index"),
        schema="rag",
    )

    # Generated so the keyword index can never drift from the content.
    # 'simple' not 'english': Postgres has no Odia configuration, and English
    # stemming applied to Indic text produces nonsense.
    op.execute("""
        ALTER TABLE rag.chunks
        ADD COLUMN content_tsv TSVECTOR
        GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED
    """)

    op.create_index(
        "ix_chunks_tenant_collection", "chunks", ["tenant_id", "collection"], schema="rag"
    )
    op.execute("CREATE INDEX ix_chunks_tsv ON rag.chunks USING GIN (content_tsv)")
    op.execute("CREATE INDEX ix_chunks_trgm ON rag.chunks USING GIN (content gin_trgm_ops)")
    op.execute("""
        CREATE INDEX ix_chunks_embedding ON rag.chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    op.drop_table("chunks", schema="rag")
