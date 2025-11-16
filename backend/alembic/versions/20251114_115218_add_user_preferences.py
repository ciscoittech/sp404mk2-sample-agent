"""add user preferences

Revision ID: a1b2c3d4e5f6
Revises: da0d29d1c775
Create Date: 2025-11-14 11:52:18.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'da0d29d1c775'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_preferences table with single-row design."""
    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vibe_analysis_model', sa.String(), nullable=False, server_default='qwen/qwen3-7b-it'),
        sa.Column('auto_vibe_analysis', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('auto_audio_features', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('batch_processing_model', sa.String(), nullable=False, server_default='qwen/qwen3-7b-it'),
        sa.Column('batch_auto_analyze', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('max_cost_per_request', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default preferences row (id=1)
    op.execute("""
        INSERT INTO user_preferences (
            id,
            vibe_analysis_model,
            auto_vibe_analysis,
            auto_audio_features,
            batch_processing_model,
            batch_auto_analyze,
            max_cost_per_request
        ) VALUES (
            1,
            'qwen/qwen3-7b-it',
            1,
            1,
            'qwen/qwen3-7b-it',
            0,
            NULL
        )
    """)


def downgrade() -> None:
    """Drop user_preferences table."""
    op.drop_table('user_preferences')
