"""add weak topic practice (user_topics, practice_topic_id, user counters)

Revision ID: f1a9c3e5b7d2
Revises: e7c2b9f4d6a1
Create Date: 2026-08-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a9c3e5b7d2'
down_revision: Union[str, Sequence[str], None] = 'e7c2b9f4d6a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_topics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(), nullable=False),
        sa.Column('times_flagged', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_topics_id'), 'user_topics', ['id'], unique=False)
    op.create_index(op.f('ix_user_topics_user_id'), 'user_topics', ['user_id'], unique=False)

    op.add_column(
        'interview_sessions',
        sa.Column('practice_topic_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_interview_sessions_practice_topic_id',
        'interview_sessions', 'user_topics',
        ['practice_topic_id'], ['id'],
    )

    op.add_column(
        'users',
        sa.Column('weak_topics_flagged_total', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column(
        'users',
        sa.Column('weak_topics_resolved_total', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'weak_topics_resolved_total')
    op.drop_column('users', 'weak_topics_flagged_total')

    op.drop_constraint('fk_interview_sessions_practice_topic_id', 'interview_sessions', type_='foreignkey')
    op.drop_column('interview_sessions', 'practice_topic_id')

    op.drop_index(op.f('ix_user_topics_user_id'), table_name='user_topics')
    op.drop_index(op.f('ix_user_topics_id'), table_name='user_topics')
    op.drop_table('user_topics')
