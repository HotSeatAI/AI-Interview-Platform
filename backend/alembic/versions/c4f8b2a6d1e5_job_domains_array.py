"""job domains array

Revision ID: c4f8b2a6d1e5
Revises: b3e6a1f7c2d9
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c4f8b2a6d1e5'
down_revision: Union[str, Sequence[str], None] = 'b3e6a1f7c2d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('users', 'job_domain')
    op.add_column(
        'users',
        sa.Column('job_domains', postgresql.ARRAY(sa.String()), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'job_domains')
    op.add_column('users', sa.Column('job_domain', sa.String(), nullable=True))
