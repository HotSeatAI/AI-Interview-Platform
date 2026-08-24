"""add resume evidence vectors

Revision ID: d3e9f6b1a204
Revises: c2d8e4f9a1b6
Create Date: 2026-08-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'd3e9f6b1a204'
down_revision: Union[str, Sequence[str], None] = 'c2d8e4f9a1b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "resume_evidence_vectors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("section", sa.String(), nullable=False),
        sa.Column("embedding", Vector(3072), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_resume_evidence_vectors_id"),
        "resume_evidence_vectors",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_resume_evidence_vectors_resume_id"),
        "resume_evidence_vectors",
        ["resume_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_resume_evidence_vectors_resume_id"),
        table_name="resume_evidence_vectors",
    )

    op.drop_index(
        op.f("ix_resume_evidence_vectors_id"),
        table_name="resume_evidence_vectors",
    )

    op.drop_table("resume_evidence_vectors")
