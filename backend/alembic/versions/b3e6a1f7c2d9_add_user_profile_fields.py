"""add user profile fields

Revision ID: b3e6a1f7c2d9
Revises: a8f3d1c9e6b4
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3e6a1f7c2d9'
down_revision: Union[str, Sequence[str], None] = 'a8f3d1c9e6b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('mobile_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('users', sa.Column('institute_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('year_of_passout', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('job_domain', sa.String(), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(), nullable=True))
    op.add_column('users', sa.Column('years_of_experience', sa.Float(), nullable=True))
    op.add_column(
        'users',
        sa.Column(
            'profile_completed',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'profile_completed')
    op.drop_column('users', 'years_of_experience')
    op.drop_column('users', 'city')
    op.drop_column('users', 'country')
    op.drop_column('users', 'job_domain')
    op.drop_column('users', 'year_of_passout')
    op.drop_column('users', 'institute_name')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'mobile_number')
    op.drop_column('users', 'full_name')
