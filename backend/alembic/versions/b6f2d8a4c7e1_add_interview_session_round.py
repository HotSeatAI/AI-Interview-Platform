"""add round to interview_sessions

Revision ID: b6f2d8a4c7e1
Revises: 8d5a48692006
Create Date: 2026-09-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6f2d8a4c7e1'
down_revision: Union[str, Sequence[str], None] = '8d5a48692006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('interview_sessions', sa.Column('round', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interview_sessions', 'round')
