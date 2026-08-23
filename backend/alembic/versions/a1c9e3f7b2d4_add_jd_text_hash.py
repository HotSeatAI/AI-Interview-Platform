"""add jd text hash

Revision ID: a1c9e3f7b2d4
Revises: 7f4c0f363791
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c9e3f7b2d4'
down_revision: Union[str, Sequence[str], None] = '7f4c0f363791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('resume_analyses', sa.Column('jd_text_hash', sa.String(), nullable=True))
    op.create_index(op.f('ix_resume_analyses_jd_text_hash'), 'resume_analyses', ['jd_text_hash'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_resume_analyses_jd_text_hash'), table_name='resume_analyses')
    op.drop_column('resume_analyses', 'jd_text_hash')
