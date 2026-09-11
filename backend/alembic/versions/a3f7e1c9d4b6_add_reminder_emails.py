"""add users.created_at, users.last_login_at, reminder_email_log

Revision ID: a3f7e1c9d4b6
Revises: b6f2d8a4c7e1
Create Date: 2026-09-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f7e1c9d4b6'
down_revision: Union[str, Sequence[str], None] = 'b6f2d8a4c7e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.add_column(
        'users',
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'reminder_email_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reminder_type', sa.String(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reminder_email_log_id'), 'reminder_email_log', ['id'], unique=False)
    op.create_index(
        'ix_reminder_email_log_user_id_sent_at',
        'reminder_email_log', ['user_id', 'sent_at'], unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_reminder_email_log_user_id_sent_at', table_name='reminder_email_log')
    op.drop_index(op.f('ix_reminder_email_log_id'), table_name='reminder_email_log')
    op.drop_table('reminder_email_log')

    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'created_at')
