from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
)

from app.database.database import Base


class UsageCounter(Base):
    """
    One row per user, tracking how many interviews/tailorings
    they've used in their CURRENT billing period. Reset in place
    (not append-only) when quota_service.check_and_consume_quota
    detects the period has rolled over - mirrors Subscription's
    current-period fields, which drive when that reset happens.

    period_end is null for the free plan - a lifetime allowance
    that's never reset once consumed.
    """

    __tablename__ = "usage_counters"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    interviews_used = Column(
        Integer,
        nullable=False,
        default=0,
    )

    tailorings_used = Column(
        Integer,
        nullable=False,
        default=0,
    )

    period_start = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    period_end = Column(
        DateTime,
        nullable=True,
    )
