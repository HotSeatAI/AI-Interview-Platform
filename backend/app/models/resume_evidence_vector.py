from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database.database import Base

# Must match the output dimensionality of GEMINI_EMBEDDING_MODEL
# (gemini-embedding-001 -> 3072). Changing the embedding model to
# one with a different dimension requires a migration to match.
EMBEDDING_DIMENSIONS = 3072


class ResumeEvidenceVector(Base):
    """
    One row per atomic evidence line extracted from a resume
    (a skill's evidence, an experience/project bullet, a
    top-level evidence claim), with its embedding — the RAG
    retrieval index used to find resume evidence that means the
    same thing as a JD requirement even when it shares no
    keywords with it.

    Populated once per resume (see
    app.services.embedding_service.ensure_resume_evidence_vectors)
    and reused across every analysis of that resume, mirroring
    how resume_profile_json is already cached and reused.
    """

    __tablename__ = "resume_evidence_vectors"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_text = Column(
        Text,
        nullable=False,
    )

    section = Column(
        String,
        nullable=False,
    )

    embedding = Column(
        Vector(EMBEDDING_DIMENSIONS),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
