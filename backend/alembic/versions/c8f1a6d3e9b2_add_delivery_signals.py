"""add delivery signals to answers

Revision ID: c8f1a6d3e9b2
Revises: b7e1c4a9d3f6
Create Date: 2026-08-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f1a6d3e9b2'
down_revision: Union[str, Sequence[str], None] = 'b7e1c4a9d3f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('answers', sa.Column('delivery_signals', sa.JSON(), nullable=True))
    op.add_column('answers', sa.Column('delivery_feedback', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('answers', 'delivery_feedback')
    op.drop_column('answers', 'delivery_signals')
