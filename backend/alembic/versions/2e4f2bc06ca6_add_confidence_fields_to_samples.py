"""add_confidence_fields_to_samples

Revision ID: 2e4f2bc06ca6
Revises: 1419beeb89a6
Create Date: 2025-11-16 11:05:47.070049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e4f2bc06ca6'
down_revision: Union[str, Sequence[str], None] = '1419beeb89a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add confidence score fields and analysis_metadata to samples table."""
    # Add confidence score columns (0-100 integer scale)
    op.add_column('samples', sa.Column('bpm_confidence', sa.Integer(), nullable=True, comment='BPM detection confidence score (0-100)'))
    op.add_column('samples', sa.Column('genre_confidence', sa.Integer(), nullable=True, comment='Genre classification confidence score (0-100)'))
    op.add_column('samples', sa.Column('key_confidence', sa.Integer(), nullable=True, comment='Musical key detection confidence score (0-100)'))

    # Add analysis metadata JSON column
    op.add_column('samples', sa.Column('analysis_metadata', sa.JSON(), nullable=True, comment='Analysis details: analyzer used, method, raw values, corrections applied'))


def downgrade() -> None:
    """Remove confidence score fields and analysis_metadata from samples table."""
    # Drop columns in reverse order
    op.drop_column('samples', 'analysis_metadata')
    op.drop_column('samples', 'key_confidence')
    op.drop_column('samples', 'genre_confidence')
    op.drop_column('samples', 'bpm_confidence')
