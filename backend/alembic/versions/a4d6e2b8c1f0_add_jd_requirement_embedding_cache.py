"""add jd requirement embedding cache

Revision ID: a4d6e2b8c1f0
Revises: f3a7c9e1b5d8
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4d6e2b8c1f0'
down_revision: Union[str, Sequence[str], None] = 'f3a7c9e1b5d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('jd_profile_cache', sa.Column('requirement_embeddings_json', sa.Text(), nullable=True))
    op.add_column('jd_profile_cache', sa.Column('embedding_model', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jd_profile_cache', 'embedding_model')
    op.drop_column('jd_profile_cache', 'requirement_embeddings_json')
