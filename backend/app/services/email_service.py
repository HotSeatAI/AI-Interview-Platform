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

    def send_email_change_notice(
        self,
        recipient_email: str,
        recipient_name: str,
        new_email: str,
    ):
        """Sent to the OLD address when an email change is requested.

        Defense-in-depth: if a session/device was compromised and
        used to request this change, the real owner still has a
        live channel (their current inbox) to notice and react
        before the new address is ever confirmed.
        """

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

            subject="Your Hot Seat account email is being changed",

            html_content=f"""
            <h2>Email change requested</h2>

            <p>
            A request was made to change the email on your Hot Seat
            account from this address to <b>{new_email}</b>.
            </p>

            <p>
            The change will only take effect once that new address
            is verified. If you did not request this, your password
            may be compromised - reset it immediately and contact
            support.
            </p>
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send email change notice: {error}"
            )

    def send_email_change_confirmation(
        self,
        recipient_email: str,
        recipient_name: str,
        change_token: str,
    ):
        """Sent to the NEW address - clicking this is what actually
        proves ownership and lets the email change take effect."""

        confirm_url = (
            f"{FRONTEND_URL}"
            f"/confirm-email-change?token={change_token}"
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

            subject="Confirm your new Hot Seat email address",

            html_content=f"""
            <h2>Confirm your new email address</h2>

            <p>
            Click the button below to confirm this address as your
            new Hot Seat account email.
            </p>

            <a
                href="{confirm_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Confirm Email Change
            </a>

            <br><br>

            <p>
            This link expires in 1 hour. You will need to log in
            again with this new address afterwards.
            </p>

            <p>
            If you did not request this, you can safely ignore this
            email - your account email will not change.
            </p>
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send email change confirmation: {error}"
            )

    def send_password_changed_notice(
        self,
        recipient_email: str,
        recipient_name: str,
    ):
        """Sent after a successful password change - same
        defense-in-depth rationale as send_email_change_notice."""

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

            subject="Your Hot Seat password was changed",

            html_content=f"""
            <h2>Password changed</h2>

            <p>
            The password on your Hot Seat account was just changed.
            </p>

            <p>
            If you did not make this change, contact support
            immediately.
            </p>
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send password changed notice: {error}"
            )