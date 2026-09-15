"""add target_id to reminder_email_log

Revision ID: c1d5b8f3a297
Revises: a3f7e1c9d4b6
Create Date: 2026-09-11 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d5b8f3a297'
down_revision: Union[str, Sequence[str], None] = 'a3f7e1c9d4b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'reminder_email_log',
        sa.Column('target_id', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('reminder_email_log', 'target_id')
