from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import PLAN_CATALOG
from app.core.permissions import require_admin
from app.database.database import get_db
from app.models.user import User
from app.services.quota_service import (
    get_or_create_subscription,
    get_or_create_usage_counter,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


class SetPlanRequest(BaseModel):
    plan: str


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):

    users = db.query(User).order_by(User.id).all()

    results = []

    for user in users:

        subscription = get_or_create_subscription(db, user)
        counter = get_or_create_usage_counter(db, user)

        plan_config = PLAN_CATALOG.get(
            subscription.plan,
            PLAN_CATALOG["free"],
        )

        results.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "plan": subscription.plan,
                "status": subscription.status,
                "interviews_used": counter.interviews_used,
                "interviews_limit": plan_config["interview_limit"],
                "tailorings_used": counter.tailorings_used,
                "tailorings_limit": plan_config["tailoring_limit"],
            }
        )

    return results


@router.patch("/users/{user_id}/plan")
def set_user_plan(
    user_id: int,
    payload: SetPlanRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Manual plan assignment - covers comped accounts and sales-
    assisted upgrades (institutional deals, support gestures)
    without needing a Razorpay checkout at all.
    """

    if payload.plan not in PLAN_CATALOG:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown plan '{payload.plan}'.",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    subscription = get_or_create_subscription(db, user)
    counter = get_or_create_usage_counter(db, user)

    subscription.plan = payload.plan
    subscription.status = "active"
    subscription.current_period_start = datetime.utcnow()

    # Admin-assigned paid plans still refill monthly like a real
    # subscription (quota_service's self-healing rollover extends
    # any "active" subscription on period end, with no Razorpay
    # webhook required) - only "free" is a true one-time lifetime
    # allowance. To revoke a comp, set the plan back to "free".
    subscription.current_period_end = (
        None
        if payload.plan == "free"
        else datetime.utcnow() + timedelta(days=30)
    )

    # Clean slate on a plan change - carrying over usage counted
    # against the OLD plan's limits could immediately re-block a
    # user an admin just upgraded (e.g. 15/15 used on Max, downgraded
    # to Starter's limit of 5).
    counter.interviews_used = 0
    counter.tailorings_used = 0
    counter.period_start = subscription.current_period_start
    counter.period_end = subscription.current_period_end

    db.commit()

    return {
        "id": user.id,
        "plan": subscription.plan,
        "status": subscription.status,
    }
