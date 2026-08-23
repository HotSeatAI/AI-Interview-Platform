"""add resume profile json

Revision ID: c2d8e4f9a1b6
Revises: a1c9e3f7b2d4
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2d8e4f9a1b6'
down_revision: Union[str, Sequence[str], None] = 'a1c9e3f7b2d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('resume_analyses', sa.Column('resume_profile_json', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('resume_analyses', 'resume_profile_json')
