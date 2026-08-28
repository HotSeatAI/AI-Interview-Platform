"""add finished_at to interview_sessions

Revision ID: e7c2b9f4d6a1
Revises: c8f1a6d3e9b2
Create Date: 2026-08-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7c2b9f4d6a1'
down_revision: Union[str, Sequence[str], None] = 'c8f1a6d3e9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('interview_sessions', sa.Column('finished_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interview_sessions', 'finished_at')
