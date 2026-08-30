"""add jd profile cache

Revision ID: f3a7c9e1b5d8
Revises: e5a2b6c1f9d3
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a7c9e1b5d8'
down_revision: Union[str, Sequence[str], None] = 'e5a2b6c1f9d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'jd_profile_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jd_text_hash', sa.String(), nullable=False),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('jd_profile_json', sa.Text(), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_jd_profile_cache_id'), 'jd_profile_cache', ['id'], unique=False)
    op.create_index(op.f('ix_jd_profile_cache_jd_text_hash'), 'jd_profile_cache', ['jd_text_hash'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_jd_profile_cache_jd_text_hash'), table_name='jd_profile_cache')
    op.drop_index(op.f('ix_jd_profile_cache_id'), table_name='jd_profile_cache')
    op.drop_table('jd_profile_cache')
