from datetime import datetime

from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import GOOGLE_CLIENT_ID
from app.models.user import User
from app.utils.jwt_handler import create_access_token


def authenticate_google_user(
    google_id_token: str,
    db: Session
):
    """
    Verify a Google ID Token, link or create the user,
    and return the application's JWT.
    """

    try:
        token_info = id_token.verify_oauth2_token(
            google_id_token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

    except GoogleAuthError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID Token"
        )

    # Ensure Google has verified the user's email.
    if not token_info.get("email_verified", False):
        raise HTTPException(
            status_code=401,
            detail="Google email is not verified"
        )

    google_user_id = token_info["sub"]
    email = token_info["email"]
    username = token_info.get(
        "name",
        email.split("@")[0]
    )

    # --------------------------------------------------
    # Case 1:
    # Existing Google account
    # --------------------------------------------------

    user = (
        db.query(User)
        .filter(User.google_id == google_user_id)
        .first()
    )

    if user:

        user.last_login_at = datetime.utcnow()
        db.commit()

        access_token = create_access_token(
            {
                "sub": user.email
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    # --------------------------------------------------
    # Case 2:
    # Existing local account with same email
    # Link Google account
    # --------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user:

        # Security check:
        # If the account is already linked to a different
        # Google account, reject the login.
        if (
            user.google_id is not None
            and user.google_id != google_user_id
        ):
            raise HTTPException(
                status_code=400,
                detail="This account is already linked to another Google account."
            )

        # First-time Google login for an existing local account.
        if user.google_id is None:
            user.google_id = google_user_id

        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        access_token = create_access_token(
            {
                "sub": user.email
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    # --------------------------------------------------
    # Case 3:
    # Brand-new Google user
    # --------------------------------------------------

    new_user = User(
        username=username,
        email=email,
        hashed_password=None,
        google_id=google_user_id,
        auth_provider="google",
        last_login_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(
        {
            "sub": new_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }