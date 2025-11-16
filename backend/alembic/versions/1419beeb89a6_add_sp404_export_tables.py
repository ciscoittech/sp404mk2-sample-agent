"""add sp404 export tables and preferences

Revision ID: 1419beeb89a6
Revises: a1b2c3d4e5f6
Create Date: 2025-11-14 16:00:10.184906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '1419beeb89a6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create SP-404 export tables and add user preference columns."""
    # Create sp404_exports table for tracking export operations
    op.create_table(
        'sp404_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('export_type', sa.String(), nullable=False),
        sa.Column('sample_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('output_path', sa.String(), nullable=False),
        sa.Column('organized_by', sa.String(), nullable=True, server_default='flat'),
        sa.Column('format', sa.String(), nullable=False, server_default='wav'),
        sa.Column('total_size_bytes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('export_duration_seconds', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create sp404_export_samples table for individual exported samples
    op.create_table(
        'sp404_export_samples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('export_id', sa.Integer(), nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=False),
        sa.Column('output_filename', sa.String(), nullable=False),
        sa.Column('conversion_successful', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('conversion_error', sa.String(), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('conversion_time_seconds', sa.Float(), nullable=True, server_default='0.0'),
        sa.ForeignKeyConstraint(['export_id'], ['sp404_exports.id'], ),
        sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('ix_sp404_exports_user_id', 'sp404_exports', ['user_id'])
    op.create_index('ix_sp404_exports_created_at', 'sp404_exports', ['created_at'])
    op.create_index('ix_sp404_export_samples_export_id', 'sp404_export_samples', ['export_id'])

    # Add SP-404 export preferences to user_preferences table
    op.add_column('user_preferences',
        sa.Column('default_export_format', sa.String(), nullable=False, server_default='wav'))
    op.add_column('user_preferences',
        sa.Column('default_export_organization', sa.String(), nullable=False, server_default='flat'))
    op.add_column('user_preferences',
        sa.Column('auto_sanitize_filenames', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    """Drop SP-404 export tables and preference columns."""
    # Remove columns from user_preferences
    op.drop_column('user_preferences', 'auto_sanitize_filenames')
    op.drop_column('user_preferences', 'default_export_organization')
    op.drop_column('user_preferences', 'default_export_format')

    # Drop indexes
    op.drop_index('ix_sp404_export_samples_export_id')
    op.drop_index('ix_sp404_exports_created_at')
    op.drop_index('ix_sp404_exports_user_id')

    # Drop tables
    op.drop_table('sp404_export_samples')
    op.drop_table('sp404_exports')
