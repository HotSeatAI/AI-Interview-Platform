"""add ats_score and ats_report_json to resume_analyses

Revision ID: a8f3d1c9e6b4
Revises: f1a9c3e5b7d2
Create Date: 2026-08-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8f3d1c9e6b4'
down_revision: Union[str, Sequence[str], None] = 'f1a9c3e5b7d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'resume_analyses',
        sa.Column('ats_score', sa.Float(), nullable=True),
    )
    op.add_column(
        'resume_analyses',
        sa.Column('ats_report_json', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('resume_analyses', 'ats_report_json')
    op.drop_column('resume_analyses', 'ats_score')
