from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status
from sqlalchemy.orm import Session
from fastapi import Query
from app.core.rate_limiter import limiter
from app.database.database import get_db
from app.models.user import User
from app.services.email_service import EmailService
from app.schemas.user import (
    UserCreate,
    UserResponse,
    ProfileUpdate,
    GoogleLoginRequest
)
from app.services.email_verification_service import (
    EmailVerificationService,
)
from app.services.password_reset_service import (
    PasswordResetService,
)
from app.utils.security import (
    hash_password,
    verify_password
)
from app.schemas.user import (
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.jwt_handler import (
    create_access_token,
    get_current_user
)

from app.services.oauth_service import (
    authenticate_google_user
)

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
    )
@limiter.limit("5/minute")
def signup(
    request: Request,
    response: Response,
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(
            user.password
        ),
        auth_provider="local",
        email_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = (
        EmailVerificationService.generate_verification_token(
            db=db,
            user_id=new_user.id,
        )
    )

    EmailService().send_verification_email(
        recipient_email=new_user.email,
        recipient_name=new_user.username,
        verification_token=verification_token,
    )

    return {
        "message":
            "Account created successfully. Please check your email to verify your account."
    }


@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if user.hashed_password is None:
        raise HTTPException(
            status_code=401,
            detail="This account was created using Google Sign-In. Please continue with Google."
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    if (
    user.auth_provider == "local"
    and not user.email_verified
):
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in."
    )

    access_token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/auth/google")
@limiter.limit("10/minute")
def google_auth(
    request: Request,
    response: Response,
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    return authenticate_google_user(
        payload.id_token,
        db
    )
@router.get("/auth/verify-email")
def verify_email(
    token: str = Query(...),
    db: Session = Depends(get_db),
):

    user = EmailVerificationService.verify_token(
        db=db,
        token=token,
    )

    return {
        "message": "Email verified successfully.",
        "email": user.email,
    }
@router.post("/auth/resend-verification")
@limiter.limit("5/minute")
def resend_verification_email(
    request: Request,
    response: Response,
    payload: ResendVerificationRequest,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    # Never reveal whether the email exists
    if (
        user is None
        or user.auth_provider != "local"
        or user.email_verified
    ):
        return {
            "message": (
                "If your account requires verification, "
                "a verification email has been sent."
            )
        }

    verification_token = (
        EmailVerificationService.generate_verification_token(
            db=db,
            user_id=user.id,
        )
    )

    EmailService().send_verification_email(
        recipient_email=user.email,
        recipient_name=user.username,
        verification_token=verification_token,
    )

    return {
        "message": (
            "If your account requires verification, "
            "a verification email has been sent."
        )
    }
@router.post("/auth/forgot-password")
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    response: Response,
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Starts a password reset for a local account.

    Always returns the same generic response, regardless of
    whether the email exists, belongs to a Google account, or
    belongs to an unverified local account - this endpoint must
    not reveal account existence or provider.

    Policy: password reset is allowed even if the account has
    not completed email verification yet. Resetting a password
    does not itself grant access - the existing /login check
    (auth_provider == "local" and not email_verified) still
    blocks sign-in afterwards, so this cannot be used to bypass
    email verification.
    """

    generic_response = {
        "message": (
            "If an eligible account exists for this email, "
            "password reset instructions have been sent."
        )
    }

    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if user is None or user.auth_provider != "local":
        return generic_response

    reset_token = (
        PasswordResetService.generate_reset_token(
            db=db,
            user_id=user.id,
        )
    )

    EmailService().send_password_reset_email(
        recipient_email=user.email,
        recipient_name=user.username,
        reset_token=reset_token,
    )

    return generic_response


@router.post("/auth/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    response: Response,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):

    user, reset_record = (
        PasswordResetService.verify_reset_token(
            db=db,
            token=payload.token,
        )
    )

    user.hashed_password = hash_password(
        payload.new_password
    )

    db.delete(reset_record)

    db.commit()

    return {
        "message": (
            "Password reset successfully. "
            "You can now log in with your new password."
        )
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def read_me(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user


@router.put(
    "/me/profile",
    response_model=UserResponse
)
def update_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.full_name = profile.full_name
    current_user.gender = profile.gender
    current_user.job_domains = profile.job_domains
    current_user.years_of_experience = profile.years_of_experience
    current_user.mobile_number = profile.mobile_number
    current_user.institute_name = profile.institute_name
    current_user.year_of_passout = profile.year_of_passout
    current_user.country = profile.country
    current_user.city = profile.city
    current_user.profile_completed = True

    db.commit()
    db.refresh(current_user)

    return current_user


@router.put(
    "/me/accept-terms",
    response_model=UserResponse
)
def accept_terms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.terms_accepted = True
    current_user.terms_accepted_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    return current_user