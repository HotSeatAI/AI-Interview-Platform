"""add plans, usage counters, and admin role

Revision ID: b7e1c4a9d3f6
Revises: a4d6e2b8c1f0
Create Date: 2026-08-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e1c4a9d3f6'
down_revision: Union[str, Sequence[str], None] = 'a4d6e2b8c1f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('role', sa.String(), nullable=False, server_default='user'),
    )

    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('razorpay_customer_id', sa.String(), nullable=True),
        sa.Column('razorpay_subscription_id', sa.String(), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=False),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=True)

    op.create_table(
        'usage_counters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('interviews_used', sa.Integer(), nullable=False),
        sa.Column('tailorings_used', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_usage_counters_id'), 'usage_counters', ['id'], unique=False)
    op.create_index(op.f('ix_usage_counters_user_id'), 'usage_counters', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_usage_counters_user_id'), table_name='usage_counters')
    op.drop_index(op.f('ix_usage_counters_id'), table_name='usage_counters')
    op.drop_table('usage_counters')

    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')

    op.drop_column('users', 'role')
