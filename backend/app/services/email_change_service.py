from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.email_change_token import (
    EmailChangeToken,
)
from app.models.user import User


class EmailChangeService:
    """
    Handles email change tokens for local accounts.

    Deliberately separate from EmailVerificationService/
    PasswordResetService: a leaked token from one flow must never
    be usable against another, and this flow also needs to carry
    the pending new_email, which the other token tables have no
    column for.

    The DB email column is never written by request_email_change -
    only verify_email_change_token's caller, after confirming
    ownership of the new address, may write it. This is the
    control that keeps Google's email-matched account linking
    (see oauth_service.py) from being abusable via an unverified
    email edit.
    """

    TOKEN_EXPIRY_HOURS = 1

    @staticmethod
    def request_email_change(
        db: Session,
        user: User,
        new_email: str,
    ) -> str:
        """
        Generates a secure email-change token, stores its SHA-256
        hash plus the pending new_email, and returns the original
        token (only the caller sees the raw value - it is emailed,
        never stored).

        Any previous pending change for this user is invalidated
        first, so only the most recently requested link works.
        """

        existing = (
            db.query(User)
            .filter(User.email == new_email)
            .first()
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail="That email address is already in use.",
            )

        db.query(
            EmailChangeToken
        ).filter(
            EmailChangeToken.user_id == user.id
        ).delete()

        token = secrets.token_urlsafe(32)

        token_hash = EmailChangeService.hash_token(
            token
        )

        change_token = EmailChangeToken(
            user_id=user.id,
            token=token_hash,
            new_email=new_email,
            expires_at=datetime.utcnow()
            + timedelta(
                hours=EmailChangeService.TOKEN_EXPIRY_HOURS
            ),
        )

        db.add(change_token)
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
    def verify_email_change_token(
        db: Session,
        token: str,
    ) -> tuple[User, EmailChangeToken]:
        """
        Validates an email-change token.

        Returns (user, token_record) if valid. The caller is
        responsible for deleting token_record after users.email
        has actually been written, so a validation-only check
        never consumes the token.

        Re-checks new_email uniqueness here too, since time has
        passed since the request was made (another account may
        have claimed the address in the meantime).
        """

        token_hash = EmailChangeService.hash_token(
            token
        )

        change_record = (
            db.query(
                EmailChangeToken
            )
            .filter(
                EmailChangeToken.token == token_hash
            )
            .first()
        )

        if change_record is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired email change link.",
            )

        if change_record.expires_at < datetime.utcnow():

            db.delete(change_record)
            db.commit()

            raise HTTPException(
                status_code=400,
                detail="This email change link has expired. Please request a new one.",
            )

        user = (
            db.query(User)
            .filter(
                User.id == change_record.user_id
            )
            .first()
        )

        if user is None:

            db.delete(change_record)
            db.commit()

            raise HTTPException(
                status_code=400,
                detail="Invalid or expired email change link.",
            )

        still_available = (
            db.query(User)
            .filter(
                User.email == change_record.new_email,
                User.id != user.id,
            )
            .first()
        )

        if still_available is not None:

            db.delete(change_record)
            db.commit()

            raise HTTPException(
                status_code=409,
                detail="That email address is already in use.",
            )

        return user, change_record
