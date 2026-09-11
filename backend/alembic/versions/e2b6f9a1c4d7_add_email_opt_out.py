"""add users.email_opt_out

Revision ID: e2b6f9a1c4d7
Revises: c1d5b8f3a297
Create Date: 2026-09-11 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2b6f9a1c4d7'
down_revision: Union[str, Sequence[str], None] = 'c1d5b8f3a297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('email_opt_out', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'email_opt_out')
