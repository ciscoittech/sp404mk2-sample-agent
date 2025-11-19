"""add_collections_system

Revision ID: 20251117_000000
Revises: 20251116_184500
Create Date: 2025-11-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251117_000000'
down_revision: Union[str, Sequence[str], None] = '20251116_184500'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create collections and collection_samples tables."""
    # Create collections table
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('parent_collection_id', sa.Integer(), nullable=True),
        sa.Column('is_smart', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('smart_rules', sa.JSON(), nullable=True),
        sa.Column('sample_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['parent_collection_id'], ['collections.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes on collections
    op.create_index('idx_collections_user_id', 'collections', ['user_id'], unique=False)
    op.create_index('idx_collections_is_smart', 'collections', ['is_smart'], unique=False)
    op.create_index('idx_collections_parent_collection_id', 'collections', ['parent_collection_id'], unique=False)

    # Create collection_samples junction table
    op.create_table(
        'collection_samples',
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('collection_id', 'sample_id'),
        sa.UniqueConstraint('collection_id', 'sample_id', name='uq_collection_sample')
    )

    # Create indexes on collection_samples
    op.create_index('idx_collection_samples_collection_id', 'collection_samples', ['collection_id'], unique=False)
    op.create_index('idx_collection_samples_sample_id', 'collection_samples', ['sample_id'], unique=False)


def downgrade() -> None:
    """Drop collections and collection_samples tables."""
    # Drop collection_samples table and its indexes
    op.drop_index('idx_collection_samples_sample_id', table_name='collection_samples')
    op.drop_index('idx_collection_samples_collection_id', table_name='collection_samples')
    op.drop_table('collection_samples')

    # Drop collections table and its indexes
    op.drop_index('idx_collections_parent_collection_id', table_name='collections')
    op.drop_index('idx_collections_is_smart', table_name='collections')
    op.drop_index('idx_collections_user_id', table_name='collections')
    op.drop_table('collections')
