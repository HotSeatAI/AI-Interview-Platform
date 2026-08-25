from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.password_reset_token import (
    PasswordResetToken,
)
from app.models.user import User


class PasswordResetService:
    """
    Handles password reset tokens for local accounts.

    Deliberately separate from EmailVerificationService:
    a leaked/expired email-verification token must never be
    usable to reset a password, and vice versa.
    """

    TOKEN_EXPIRY_HOURS = 1

    @staticmethod
    def generate_reset_token(
        db: Session,
        user_id: int,
    ) -> str:
        """
        Generates a secure password reset token, stores its
        SHA-256 hash, and returns the original token (only the
        caller sees the raw value - it is emailed, never stored).

        Any previous reset tokens for this user are invalidated
        first, so only the most recently requested link works.
        """

        db.query(
            PasswordResetToken
        ).filter(
            PasswordResetToken.user_id == user_id
        ).delete()

        token = secrets.token_urlsafe(32)

        token_hash = PasswordResetService.hash_token(
            token
        )

        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token_hash,
            expires_at=datetime.utcnow()
            + timedelta(
                hours=PasswordResetService.TOKEN_EXPIRY_HOURS
            ),
        )

        db.add(reset_token)
        db.commit()

        return token

    @staticmethod
    def hash_token(
        token: str,
    ) -> str:

        return hashlib.sha256(
            token.encode()
        ).hexdigest()

    @staticmethod
    def verify_reset_token(
        db: Session,
        token: str,
    ) -> tuple[User, PasswordResetToken]:
        """
        Validates a password reset token.

        Returns (user, token_record) if valid. The caller is
        responsible for deleting token_record after the password
        has actually been changed, so a validation-only check
        never consumes the token.
        """

        token_hash = PasswordResetService.hash_token(
            token
        )

        reset_record = (
            db.query(
                PasswordResetToken
            )
            .filter(
                PasswordResetToken.token == token_hash
            )
            .first()
        )

        if reset_record is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired password reset link.",
            )

        if reset_record.expires_at < datetime.utcnow():

            db.delete(reset_record)
            db.commit()

            raise HTTPException(
                status_code=400,
                detail="This password reset link has expired. Please request a new one.",
            )

        user = (
            db.query(User)
            .filter(
                User.id == reset_record.user_id
            )
            .first()
        )

        if user is None:

            db.delete(reset_record)
            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Invalid or expired password reset link.",
            )

        return user, reset_record
