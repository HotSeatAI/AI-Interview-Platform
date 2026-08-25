"""add question type

Revision ID: e5a2b6c1f9d3
Revises: d3e9f6b1a204
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a2b6c1f9d3'
down_revision: Union[str, Sequence[str], None] = 'd3e9f6b1a204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('questions', sa.Column('question_type', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('questions', 'question_type')
