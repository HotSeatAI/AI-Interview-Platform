from datetime import datetime, timedelta
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import PLAN_CATALOG
from app.models.subscription import Subscription
from app.models.usage_counter import UsageCounter
from app.models.user import User

Feature = Literal["interview", "tailoring"]


def get_or_create_subscription(
    db: Session,
    user: User,
) -> Subscription:

    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id)
        .first()
    )

    if subscription:
        return subscription

    subscription = Subscription(
        user_id=user.id,
        plan="free",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=None,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_or_create_usage_counter(
    db: Session,
    user: User,
) -> UsageCounter:

    counter = (
        db.query(UsageCounter)
        .filter(UsageCounter.user_id == user.id)
        .first()
    )

    if counter:
        return counter

    counter = UsageCounter(
        user_id=user.id,
        interviews_used=0,
        tailorings_used=0,
        period_start=datetime.utcnow(),
        period_end=None,
    )
    db.add(counter)
    db.commit()
    db.refresh(counter)

    return counter


def _roll_period_forward_if_elapsed(
    db: Session,
    subscription: Subscription,
    counter: UsageCounter,
) -> None:
    """
    Self-heals the billing period even if Razorpay's
    subscription.charged renewal webhook is late or never
    arrives - the counter never trusts the webhook alone for
    correctness. A no-op for the free plan (current_period_end
    is null there, meaning its allowance never resets).
    """

    if subscription.current_period_end is None:
        return

    now = datetime.utcnow()

    if now < subscription.current_period_end:
        return

    if subscription.status != "active":
        # The period they paid for has run out and Razorpay
        # never renewed it (cancelled, or repeated payment
        # failures) - drop to the free plan's lifetime allowance
        # rather than optimistically extending a subscription
        # that isn't actually being paid for anymore.
        subscription.plan = "free"
        subscription.status = "active"
        subscription.current_period_start = now
        subscription.current_period_end = None

        counter.interviews_used = 0
        counter.tailorings_used = 0
        counter.period_start = now
        counter.period_end = None

        db.commit()
        return

    # status == "active": the period elapsed but no
    # subscription.charged webhook has arrived yet - assume it's
    # just delayed (not that the renewal failed, which would have
    # flipped status to "past_due"/"cancelled" via a different
    # webhook) and extend on the same plan so access isn't
    # wrongly cut off. If the webhook never does arrive because
    # the renewal genuinely failed, the next payment.failed/
    # subscription.cancelled webhook corrects status, and this
    # function's cancelled-branch above takes over from there.
    subscription.current_period_start = now
    subscription.current_period_end = now + timedelta(days=30)

    counter.interviews_used = 0
    counter.tailorings_used = 0
    counter.period_start = subscription.current_period_start
    counter.period_end = subscription.current_period_end

    db.commit()


def check_and_consume_quota(
    db: Session,
    user: User,
    feature: Feature,
) -> int:
    """
    Raises HTTPException(402) if the user has used up their
    plan's allowance for `feature` this billing period; otherwise
    consumes one unit and returns the remaining count.

    Called at the top of the interview-generation and resume-JD-
    tailoring endpoints, before any expensive work (Gemini calls,
    DB rows for the job itself) happens - a blocked user should
    never get partway into a request that's just going to fail.
    """

    subscription = get_or_create_subscription(db, user)
    counter = get_or_create_usage_counter(db, user)

    _roll_period_forward_if_elapsed(db, subscription, counter)

    plan_config = PLAN_CATALOG.get(
        subscription.plan,
        PLAN_CATALOG["free"],
    )

    limit_key = f"{feature}_limit"
    used_attr = f"{feature}s_used"

    limit = plan_config[limit_key]
    used = getattr(counter, used_attr)

    if used >= limit:
        raise HTTPException(
            status_code=402,
            detail=(
                f"You've used all {limit} {feature}s included "
                f"in your {subscription.plan} plan"
                + (
                    " this month."
                    if subscription.current_period_end
                    else "."
                )
                + " Upgrade your plan to continue."
            ),
        )

    setattr(counter, used_attr, used + 1)
    db.commit()

    return limit - (used + 1)


def refund_quota(
    db: Session,
    user: User,
    feature: Feature,
) -> None:
    """
    Best-effort: a failed generation/analysis shouldn't cost the
    user a quota unit. Called from the failure paths in
    generate_questions and ResumeAnalysisWorker._fail. Never
    raises - a refund failure must never mask the original error
    that triggered it.
    """

    try:

        counter = (
            db.query(UsageCounter)
            .filter(UsageCounter.user_id == user.id)
            .first()
        )

        if not counter:
            return

        used_attr = f"{feature}s_used"
        used = getattr(counter, used_attr)

        if used > 0:
            setattr(counter, used_attr, used - 1)
            db.commit()

    except Exception:
        db.rollback()
