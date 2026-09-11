import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.core.config import (
    BACKEND_URL,
    BREVO_API_KEY,
    FRONTEND_URL,
    SENDER_EMAIL,
    SENDER_NAME,
)


def _unsubscribe_url(unsubscribe_token: str) -> str:
    return f"{BACKEND_URL}/unsubscribe?token={unsubscribe_token}"


def _unsubscribe_footer(unsubscribe_token: str) -> str:
    """Shared footer for reminder emails only - verification/reset/
    security emails are not marketing and never include this."""

    return f"""
    <p style="font-size:12px;color:#888;margin-top:24px;">
        Don't want these emails?
        <a href="{_unsubscribe_url(unsubscribe_token)}" style="color:#888;">Unsubscribe</a>
    </p>
    """


def _unsubscribe_headers(unsubscribe_token: str) -> dict:
    """RFC 8058 one-click unsubscribe headers. Gmail/Yahoo's 2024
    bulk-sender rules specifically look for this - a body link
    alone (no header) reads as unauthenticated bulk mail and can get
    silently dropped rather than just spam-foldered, which is worse
    for actually reaching the inbox than having no unsubscribe link
    at all. Required alongside the body link, not instead of it -
    the header handles email-client "Unsubscribe" buttons, the link
    covers clients that don't surface it."""

    return {
        "List-Unsubscribe": f"<{_unsubscribe_url(unsubscribe_token)}>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    }


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

    def send_verification_reminder_email(
        self,
        recipient_email: str,
        recipient_name: str,
        verification_token: str,
    ):
        """One-time nudge for a local signup that never verified
        their email - sent once by scripts/send_reminder_emails.py.
        Uses a fresh token (old one may have expired), same as
        resend_verification_email in api/auth.py."""

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

            subject="You're one click away from verifying your account",

            html_content=f"""
            <p>Hey {recipient_name},</p>

            <p>
            You signed up for Hot Seat, but your account is still
            unverified - you're one click away from being able to log
            in and start practicing.
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
                f"Unable to send verification reminder email: {error}"
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

    def send_reminder_highlight_email(
        self,
        recipient_email: str,
        recipient_name: str,
        last_score: float,
        weak_topic: str,
        unsubscribe_token: str,
    ):
        """Tier A reminder (~2 days inactive) - personalized with the
        user's last session score and a flagged weak topic."""

        practice_url = f"{FRONTEND_URL}/generate-interview"

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

            headers=_unsubscribe_headers(unsubscribe_token),

            subject=f"Can you beat your last score of {last_score:.0f}%?",

            html_content=f"""
            <p>Hey {recipient_name},</p>

            <p>
            Your last mock interview score was <b>{last_score:.0f}%</b>.
            Good work - but interview skills fade quickly without
            regular practice, and <b>"{weak_topic}"</b> is one spot
            that could still trip you up in a real interview.
            </p>

            <p>
            Just 10 minutes of practice today can turn that weak spot
            into a strength before it costs you.
            </p>

            <a
                href="{practice_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Beat Your Score
            </a>

            <p>&mdash; The Hot Seat Team</p>

            {_unsubscribe_footer(unsubscribe_token)}
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send reminder highlight email: {error}"
            )

    def send_reminder_feature_email(
        self,
        recipient_email: str,
        recipient_name: str,
        feature_name: str,
        feature_url: str,
        used: bool,
        unsubscribe_token: str,
    ):
        """Tier B reminder (~4 days inactive). If `used` is False,
        nudges toward an untried feature. If True (every feature's
        already been tried), recaps their most-used one instead."""

        if not used:

            subject = f"You haven't tried {feature_name} yet"

            body = f"""
            <p>Hey {recipient_name},</p>

            <p>
            You've been putting in good work on mock interviews - but
            there's one part of Hot Seat you haven't tried yet:
            <b>{feature_name}</b>.
            </p>

            <p>
            It only takes two minutes, and most people who try it find
            something useful they didn't know before.
            </p>

            <a
                href="{feature_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Try {feature_name}
            </a>

            <p>&mdash; The Hot Seat Team</p>

            {_unsubscribe_footer(unsubscribe_token)}
            """

        else:

            subject = f"Check your {feature_name} results again"

            body = f"""
            <p>Hey {recipient_name},</p>

            <p>
            Last time you used <b>{feature_name}</b>, it caught
            something specific and worth fixing - the kind of thing
            that's easy to miss on your own.
            </p>

            <p>
            Things change quickly, so it's worth running it again to
            see what's changed.
            </p>

            <a
                href="{feature_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Try {feature_name} Again
            </a>

            <p>&mdash; The Hot Seat Team</p>

            {_unsubscribe_footer(unsubscribe_token)}
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

            headers=_unsubscribe_headers(unsubscribe_token),

            subject=subject,

            html_content=body,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send reminder feature email: {error}"
            )

    def send_reminder_progress_recap_email(
        self,
        recipient_email: str,
        recipient_name: str,
        session_count: int,
        avg_score: float,
        best_domain: str,
        unsubscribe_token: str,
    ):
        """Tier C reminder (~6 days inactive) - aggregate progress
        recap, reassuring rather than guilt-tripping."""

        dashboard_url = f"{FRONTEND_URL}/dashboard"

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

            headers=_unsubscribe_headers(unsubscribe_token),

            subject="Look how far you've come",

            html_content=f"""
            <p>Hey {recipient_name},</p>

            <p>
            You've completed <b>{session_count} mock interviews</b>
            with an average score of <b>{avg_score:.0f}%</b>, and
            you're strongest in <b>{best_domain}</b>. That's real
            progress - most people give up long before getting here.
            </p>

            <p>
            Everything you've built is saved right where you left it.
            The only thing that fades from here is momentum, so don't
            let it slip.
            </p>

            <a
                href="{dashboard_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Pick Up Where You Left Off
            </a>

            <p>&mdash; The Hot Seat Team</p>

            {_unsubscribe_footer(unsubscribe_token)}
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send reminder progress recap email: {error}"
            )

    def send_unfinished_session_email(
        self,
        recipient_email: str,
        recipient_name: str,
        session_id: int,
        role: str,
        unsubscribe_token: str,
    ):
        """One-time nudge for an interview session left unfinished
        for over 2 hours."""

        session_url = f"{FRONTEND_URL}/interview/{session_id}"

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

            headers=_unsubscribe_headers(unsubscribe_token),

            subject="Finish your interview and see your score",

            html_content=f"""
            <p>Hey {recipient_name},</p>

            <p>
            You started a <b>{role}</b> interview and stepped away
            partway through - nothing was lost. Every question you
            already answered, and every one still waiting, is exactly
            where you left it.
            </p>

            <p>
            Only finished interviews get scored, so finishing now takes
            less time than starting a new one from scratch.
            </p>

            <a
                href="{session_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Finish Interview
            </a>

            <p>&mdash; The Hot Seat Team</p>

            {_unsubscribe_footer(unsubscribe_token)}
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send unfinished session email: {error}"
            )

    def send_stalled_analysis_email(
        self,
        recipient_email: str,
        recipient_name: str,
        analysis_id: int,
        job_title: str,
        unsubscribe_token: str,
    ):
        """One-time nudge for a resume analysis stuck in
        'processing'/'failed' for over an hour."""

        analysis_url = f"{FRONTEND_URL}/resume-analysis/{analysis_id}"

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

            headers=_unsubscribe_headers(unsubscribe_token),

            subject="Let's fix your resume analysis",

            html_content=f"""
            <p>Hey {recipient_name},</p>

            <p>
            We tried to analyze your resume against <b>{job_title}</b>,
            but something glitched partway through - that's on us, not
            your resume or your job description.
            </p>

            <p>
            Nothing was lost on your side, and a retry almost always
            goes through cleanly the second time.
            </p>

            <a
                href="{analysis_url}"
                style="
                    background:#2563eb;
                    color:white;
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:8px;
                "
            >
                Retry Analysis
            </a>

            <p>&mdash; The Hot Seat Team</p>

            {_unsubscribe_footer(unsubscribe_token)}
            """,
        )

        try:

            self.api_instance.send_transac_email(
                email
            )

        except ApiException as error:

            raise RuntimeError(
                f"Unable to send stalled analysis email: {error}"
            )