from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import PLAN_CATALOG
from app.database.database import get_db
from app.models.subscription import Subscription
from app.models.usage_counter import UsageCounter
from app.models.user import User
from app.services import payment_service
from app.services.quota_service import (
    get_or_create_subscription,
    get_or_create_usage_counter,
)

router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)


class CreateSubscriptionRequest(BaseModel):
    plan: str


@router.get("/me")
def get_my_billing_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    subscription = get_or_create_subscription(db, current_user)
    counter = get_or_create_usage_counter(db, current_user)

    plan_config = PLAN_CATALOG.get(
        subscription.plan,
        PLAN_CATALOG["free"],
    )

    return {
        "plan": subscription.plan,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end,
        "interviews_used": counter.interviews_used,
        "interviews_limit": plan_config["interview_limit"],
        "tailorings_used": counter.tailorings_used,
        "tailorings_limit": plan_config["tailoring_limit"],
    }


@router.post("/create-subscription")
def create_subscription(
    payload: CreateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if payload.plan not in ("starter", "pro", "max"):
        raise HTTPException(
            status_code=400,
            detail="Unknown plan.",
        )

    subscription = get_or_create_subscription(db, current_user)

    try:
        checkout = payment_service.create_subscription_checkout(
            current_user,
            subscription,
            payload.plan,
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    subscription.razorpay_customer_id = checkout[
        "razorpay_customer_id"
    ]
    db.commit()

    return checkout


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Public endpoint - Razorpay calls this server-to-server, so
    there's no current_user/JWT here. Authenticity is verified
    entirely via the HMAC signature in the X-Razorpay-Signature
    header, not by who's asking.
    """

    payload_body = await request.body()

    signature = request.headers.get("X-Razorpay-Signature", "")

    try:
        is_valid = payment_service.verify_webhook_signature(
            payload_body,
            signature,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature.",
        )

    payload = await request.json()

    event = payload.get("event")
    entity = (
        payload.get("payload", {})
        .get("subscription", {})
        .get("entity", {})
    )

    razorpay_subscription_id = entity.get("id")
    notes = entity.get("notes", {}) or {}
    user_id = notes.get("user_id")
    plan = notes.get("plan")

    if not razorpay_subscription_id or not user_id:
        # Not a subscription lifecycle event we care about
        # (Razorpay sends many other event types on the same
        # endpoint if you subscribe to more than subscription.*).
        return {"status": "ignored"}

    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == int(user_id))
        .first()
    )

    if not subscription:
        return {"status": "ignored"}

    if event in ("subscription.activated", "subscription.charged"):

        subscription.plan = plan or subscription.plan
        subscription.status = "active"
        subscription.razorpay_subscription_id = (
            razorpay_subscription_id
        )
        subscription.current_period_start = datetime.utcnow()
        subscription.current_period_end = (
            datetime.utcnow() + timedelta(days=30)
        )

        counter = get_or_create_usage_counter(
            db,
            db.query(User).filter(User.id == int(user_id)).first(),
        )
        counter.interviews_used = 0
        counter.tailorings_used = 0
        counter.period_start = subscription.current_period_start
        counter.period_end = subscription.current_period_end

        db.commit()

    elif event == "subscription.cancelled":

        subscription.status = "cancelled"
        # Downgrade takes effect at the end of the period already
        # paid for, not immediately - the self-healing rollover in
        # quota_service will drop them to "free" once
        # current_period_end passes, since a cancelled Razorpay
        # subscription won't send further subscription.charged
        # events to keep extending it.
        db.commit()

    elif event == "payment.failed":

        subscription.status = "past_due"
        db.commit()

    return {"status": "ok"}
