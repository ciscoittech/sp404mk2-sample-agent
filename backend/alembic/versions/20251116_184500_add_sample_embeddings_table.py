"""add_sample_embeddings_table

Revision ID: 20251116_184500
Revises: 2e4f2bc06ca6
Create Date: 2025-11-16 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251116_184500'
down_revision: Union[str, Sequence[str], None] = '2e4f2bc06ca6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sample_embeddings table for vector search with float arrays."""
    op.create_table(
        'sample_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=False),
        sa.Column('vibe_vector', sa.ARRAY(sa.Float()), nullable=False),
        sa.Column('embedding_source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sample_id'),
    )
    # Create index on sample_id for lookups
    op.create_index('idx_sample_embeddings_sample_id', 'sample_embeddings', ['sample_id'], unique=False)


def downgrade() -> None:
    """Drop sample_embeddings table."""
    op.drop_index('idx_sample_embeddings_sample_id', table_name='sample_embeddings')
    op.drop_table('sample_embeddings')
