"""add interview session feedback

Revision ID: f9c3a5e8d2b7
Revises: e2b6f9a1c4d7
Create Date: 2026-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9c3a5e8d2b7'
down_revision: Union[str, Sequence[str], None] = 'e2b6f9a1c4d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('interview_sessions', sa.Column('rating', sa.Integer(), nullable=True))
    op.add_column('interview_sessions', sa.Column('feedback_text', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interview_sessions', 'feedback_text')
    op.drop_column('interview_sessions', 'rating')
