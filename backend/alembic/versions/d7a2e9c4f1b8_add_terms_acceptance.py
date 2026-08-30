"""add terms acceptance

Revision ID: d7a2e9c4f1b8
Revises: c4f8b2a6d1e5
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7a2e9c4f1b8'
down_revision: Union[str, Sequence[str], None] = 'c4f8b2a6d1e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column(
            'terms_accepted',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        'users',
        sa.Column('terms_accepted_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'terms_accepted_at')
    op.drop_column('users', 'terms_accepted')
