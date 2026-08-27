import razorpay

from app.core.config import (
    PLAN_CATALOG,
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
    RAZORPAY_WEBHOOK_SECRET,
)
from app.models.subscription import Subscription
from app.models.user import User


def _get_client() -> razorpay.Client:

    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise RuntimeError(
            "RAZORPAY_KEY_ID/RAZORPAY_KEY_SECRET are not "
            "configured."
        )

    return razorpay.Client(
        auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
    )


def get_or_create_razorpay_customer(
    client: razorpay.Client,
    user: User,
    subscription: Subscription,
) -> str:
    """
    Idempotent: reuses the customer id already stored on
    `subscription` if present, otherwise creates one in Razorpay
    and returns it for the caller to persist.
    """

    if subscription.razorpay_customer_id:
        return subscription.razorpay_customer_id

    customer = client.customer.create(
        {
            "name": user.username,
            "email": user.email,
            "fail_existing": "0",
        }
    )

    return customer["id"]


def create_subscription_checkout(
    user: User,
    subscription: Subscription,
    plan: str,
) -> dict:
    """
    Creates a Razorpay Subscription for `plan` and returns the
    details the frontend needs to open Razorpay Checkout. Does
    NOT activate the subscription locally - that only happens
    once the `subscription.activated` webhook confirms payment
    actually succeeded (see billing.py).
    """

    plan_config = PLAN_CATALOG.get(plan)

    if not plan_config or not plan_config.get("razorpay_plan_id"):
        raise ValueError(
            f"'{plan}' is not a purchasable plan."
        )

    client = _get_client()

    razorpay_customer_id = get_or_create_razorpay_customer(
        client,
        user,
        subscription,
    )

    razorpay_subscription = client.subscription.create(
        {
            "plan_id": plan_config["razorpay_plan_id"],
            "customer_notify": 1,
            "total_count": 120,  # ~10 years of monthly cycles; Razorpay requires a count, not literal "forever"
            "notes": {
                "user_id": str(user.id),
                "plan": plan,
            },
        }
    )

    return {
        "razorpay_key_id": RAZORPAY_KEY_ID,
        "razorpay_customer_id": razorpay_customer_id,
        "razorpay_subscription_id": razorpay_subscription["id"],
        "plan": plan,
        "price_inr": plan_config["price_inr"],
    }


def verify_webhook_signature(
    payload_body: bytes,
    signature: str,
) -> bool:

    if not RAZORPAY_WEBHOOK_SECRET:
        raise RuntimeError(
            "RAZORPAY_WEBHOOK_SECRET is not configured."
        )

    client = _get_client()

    try:
        client.utility.verify_webhook_signature(
            payload_body.decode("utf-8"),
            signature,
            RAZORPAY_WEBHOOK_SECRET,
        )
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
