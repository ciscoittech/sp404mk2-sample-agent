"""add_sample_sources

Revision ID: 20251117_100000
Revises: 20251117_000000
Create Date: 2025-11-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251117_100000'
down_revision: Union[str, Sequence[str], None] = '20251117_000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sample_sources table for metadata tracking."""
    # Create sample_sources table
    op.create_table(
        'sample_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_url', sa.String(length=2048), nullable=True),
        sa.Column('artist', sa.String(length=255), nullable=True),
        sa.Column('album', sa.String(length=255), nullable=True),
        sa.Column('release_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('license_type', sa.String(), nullable=False, server_default='unknown'),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('import_batch_id', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['import_batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sample_id', name='uq_sample_source')
    )

    # Create indexes for performance
    op.create_index('idx_sample_sources_sample_id', 'sample_sources', ['sample_id'], unique=True)
    op.create_index('idx_sample_sources_source_type', 'sample_sources', ['source_type'], unique=False)
    op.create_index('idx_sample_sources_artist', 'sample_sources', ['artist'], unique=False)


def downgrade() -> None:
    """Drop sample_sources table."""
    # Drop indexes
    op.drop_index('idx_sample_sources_artist', table_name='sample_sources')
    op.drop_index('idx_sample_sources_source_type', table_name='sample_sources')
    op.drop_index('idx_sample_sources_sample_id', table_name='sample_sources')

    # Drop table
    op.drop_table('sample_sources')
