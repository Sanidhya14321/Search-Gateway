"""Add observability columns to agent_runs
Revision ID: 003
Revises: 002
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('agent_runs',
        sa.Column('trace_id', sa.String(32), nullable=True))
    op.add_column('agent_runs',
        sa.Column('llm_calls_count', sa.Integer(), server_default='0'))
    op.add_column('agent_runs',
        sa.Column('total_chunks_retrieved', sa.Integer(), server_default='0'))
    op.add_column('agent_runs',
        sa.Column('cache_hit', sa.Boolean(), server_default='false'))
    op.create_index('idx_agent_runs_trace', 'agent_runs', ['trace_id'])

def downgrade():
    op.drop_index('idx_agent_runs_trace')
    op.drop_column('agent_runs', 'cache_hit')
    op.drop_column('agent_runs', 'total_chunks_retrieved')
    op.drop_column('agent_runs', 'llm_calls_count')
    op.drop_column('agent_runs', 'trace_id')
