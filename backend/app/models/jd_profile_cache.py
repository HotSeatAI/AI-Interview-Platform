from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from app.database.database import Base


class JDProfileCache(Base):
    """
    Global cache of structured JD profiles, keyed only by the JD
    text's content hash - no user_id or resume_id, since JD
    structuring (job_description_parser.structure_job_description)
    is a pure function of the JD text alone. Any user submitting a
    JD whose normalized text was already structured for anyone
    else reuses this row instead of triggering another Gemini
    call. See app.services.resume_analysis_worker Step 2.
    """

    __tablename__ = "jd_profile_cache"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    jd_text_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    job_title = Column(
        String,
        nullable=True,
    )

    jd_profile_json = Column(
        Text,
        nullable=False,
    )

    # Cached RETRIEVAL_QUERY embedding vectors for this JD's
    # requirements (JSON list of float lists, same order as
    # jd_profile.requirements) - see
    # app.services.embedding_service.build_embedding_evidence_map.
    # embedding_model records which model produced them, so a
    # future embedding-model change doesn't silently mix vectors
    # from two different embedding spaces: a row whose
    # embedding_model doesn't match the current config is treated
    # as a miss and recomputed.
    requirement_embeddings_json = Column(
        Text,
        nullable=True,
    )

    embedding_model = Column(
        String,
        nullable=True,
    )

    hit_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    last_used_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
