"""create email change tokens table

Revision ID: 8d5a48692006
Revises: d7a2e9c4f1b8
Create Date: 2026-09-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d5a48692006"
down_revision: Union[str, Sequence[str], None] = "d7a2e9c4f1b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "email_change_tokens",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "token",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "new_email",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        op.f("ix_email_change_tokens_id"),
        "email_change_tokens",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_email_change_tokens_token"),
        "email_change_tokens",
        ["token"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_email_change_tokens_token"),
        table_name="email_change_tokens",
    )

    op.drop_index(
        op.f("ix_email_change_tokens_id"),
        table_name="email_change_tokens",
    )

    op.drop_table(
        "email_change_tokens",
    )
