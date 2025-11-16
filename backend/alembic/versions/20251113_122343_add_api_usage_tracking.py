"""add api usage tracking

Revision ID: da0d29d1c775
Revises: None
Create Date: 2025-11-13 12:23:43.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'da0d29d1c775'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create api_usage table
    op.create_table('api_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('operation', sa.String(), nullable=False),
        sa.Column('input_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('output_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('input_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('output_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('total_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=True),
        sa.Column('batch_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('extra_metadata', sa.JSON(), server_default='{}', nullable=True),
        sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )

    # Create indexes
    op.create_index(op.f('ix_api_usage_created_at'), 'api_usage', ['created_at'], unique=False)
    op.create_index(op.f('ix_api_usage_model'), 'api_usage', ['model'], unique=False)
    op.create_index(op.f('ix_api_usage_operation'), 'api_usage', ['operation'], unique=False)
    op.create_index(op.f('ix_api_usage_request_id'), 'api_usage', ['request_id'], unique=True)
    op.create_index(op.f('ix_api_usage_user_id'), 'api_usage', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_api_usage_user_id'), table_name='api_usage')
    op.drop_index(op.f('ix_api_usage_request_id'), table_name='api_usage')
    op.drop_index(op.f('ix_api_usage_operation'), table_name='api_usage')
    op.drop_index(op.f('ix_api_usage_model'), table_name='api_usage')
    op.drop_index(op.f('ix_api_usage_created_at'), table_name='api_usage')

    # Drop table
    op.drop_table('api_usage')
