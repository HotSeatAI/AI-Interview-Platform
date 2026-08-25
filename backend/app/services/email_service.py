import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.core.config import (
    BREVO_API_KEY,
    FRONTEND_URL,
    SENDER_EMAIL,
    SENDER_NAME,
)


class EmailService:

    def __init__(self):

        configuration = (
            sib_api_v3_sdk.Configuration()
        )

        configuration.api_key[
            "api-key"
        ] = BREVO_API_KEY

        self.api_instance = (
            sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(
                    configuration
                )
            )
        )

    def send_verification_email(
        self,
        recipient_email: str,
        recipient_name: str,
        verification_token: str,
    ):

        verification_url = (
            f"{FRONTEND_URL}"
            f"/verify-email?token={verification_token}"
        )

        email = sib_api_v3_sdk.SendSmtpEmail(

            to=[
                {
                    "email": recipient_email,
                    "name": recipient_name,
                }
            ],

            sender={
                "name": SENDER_NAME,
                "email": SENDER_EMAIL,
            },

            subject="Verify your Hot Seat account",

            html_content=f"""
            <h2>Welcome to Hot Seat!</h2>

            <p>
            Thanks for signing up.
            </p>

            <p>
            Click the button below to verify your email.
            </p>

            <a
                href="{verification_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Verify Email
            </a>

            <br><br>

            <p>
            This link expires in 24 hours.
            </p>
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send verification email: {error}"
            )

    def send_password_reset_email(
        self,
        recipient_email: str,
        recipient_name: str,
        reset_token: str,
    ):

        reset_url = (
            f"{FRONTEND_URL}"
            f"/reset-password?token={reset_token}"
        )

        email = sib_api_v3_sdk.SendSmtpEmail(

            to=[
                {
                    "email": recipient_email,
                    "name": recipient_name,
                }
            ],

            sender={
                "name": SENDER_NAME,
                "email": SENDER_EMAIL,
            },

            subject="Reset your Hot Seat password",

            html_content=f"""
            <h2>Password reset requested</h2>

            <p>
            We received a request to reset the password for
            your Hot Seat account.
            </p>

            <p>
            Click the button below to choose a new password.
            </p>

            <a
                href="{reset_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Reset Password
            </a>

            <br><br>

            <p>
            This link expires in 1 hour.
            </p>

            <p>
            If you did not request a password reset, you can
            safely ignore this email.
            </p>
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send password reset email: {error}"
            )