from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.database.database import Base


class Subscription(Base):
    """
    One row per user - the user's current plan/billing state.
    Upserted in place on plan changes/renewals rather than
    append-only, matching how the rest of this codebase models
    current state (e.g. ResumeAnalysis rows are updated in place
    as a job progresses).

    plan: "free" | "starter" | "pro" | "max" - see
    app.core.config.PLAN_CATALOG for the allowances each plan
    grants.

    status: "active" | "past_due" | "cancelled".

    current_period_end is null for the free plan (a lifetime
    allowance that never resets); for paid plans it marks when
    the usage counters next reset, driven by Razorpay's
    subscription.charged webhook and self-healed by
    quota_service if that webhook is ever late or missed.
    """

    __tablename__ = "subscriptions"

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

    plan = Column(
        String,
        nullable=False,
        default="free",
    )

    status = Column(
        String,
        nullable=False,
        default="active",
    )

    razorpay_customer_id = Column(
        String,
        nullable=True,
    )

    razorpay_subscription_id = Column(
        String,
        nullable=True,
    )

    current_period_start = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    current_period_end = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
