"""
Daily reminder-email batch job for inactive users.

Run manually or via the "reminder-emails" GitHub Actions workflow
(there is no in-process scheduler - see CLAUDE.md's note on Render's
free tier spinning the backend down when idle).

Usage:
    python -m app.scripts.send_reminder_emails [--dry-run]

Env:
    REMINDER_EMAIL_ALLOWLIST - optional comma-separated list of
        email addresses. When set, the full tier/event logic still
        runs and is logged as normal, but the actual Brevo send is
        skipped for any recipient not on the list. Used to validate
        the batch against real user data without emailing real
        users during rollout.
"""
import argparse
import os
from datetime import datetime, timedelta

from sqlalchemy import func, text

from app.core.config import FRONTEND_URL
from app.database.database import SessionLocal, engine
from app.models.answer import Answer
from app.models.interview_session import InterviewSession
from app.models.question import Question
from app.models.reminder_email_log import ReminderEmailLog
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User
from app.models.user_topic import UserTopic
from app.services.email_service import EmailService
from app.utils.jwt_handler import create_unsubscribe_token

# Not used directly below, but User.<relationship> references these
# classes by string name - importing them registers the classes on
# Base's mapper registry so SQLAlchemy can resolve those
# relationships when the User mapper is configured.
from app.models.email_verification_token import EmailVerificationToken  # noqa: F401
from app.models.password_reset_token import PasswordResetToken  # noqa: F401
from app.models.email_change_token import EmailChangeToken  # noqa: F401

COOLDOWN = timedelta(days=2)

# Checked largest-first so the biggest tier the user has crossed
# wins on any given run - see _pick_tier.
TIME_TIERS = [
    ("inactive_6d", timedelta(days=6)),
    ("inactive_4d", timedelta(days=4)),
    ("inactive_2d", timedelta(days=2)),
]

UNFINISHED_SESSION_AGE = timedelta(hours=2)
STALLED_ANALYSIS_AGE = timedelta(hours=1)
STALLED_ANALYSIS_STATUSES = ("processing", "failed")

# Arbitrary fixed key for a Postgres session-level advisory lock -
# held for the whole run so two overlapping invocations (e.g. a
# manual workflow_dispatch fired while the schedule is also running)
# can't both pass the same "not already sent" check before either
# writes its ReminderEmailLog row and double-email someone. A second
# instance that can't acquire the lock exits immediately without
# touching the DB or sending anything.
ADVISORY_LOCK_KEY = 872341


def _get_allowlist():
    raw = os.environ.get("REMINDER_EMAIL_ALLOWLIST", "")
    return {addr.strip().lower() for addr in raw.split(",") if addr.strip()}


def _last_activity(db, user):
    last_session_at = (
        db.query(func.max(InterviewSession.created_at))
        .filter(InterviewSession.user_id == user.id)
        .scalar()
    )
    last_analysis_at = (
        db.query(func.max(ResumeAnalysis.created_at))
        .filter(ResumeAnalysis.user_id == user.id)
        .scalar()
    )
    candidates = [t for t in (user.last_login_at, last_session_at, last_analysis_at) if t]
    return max(candidates) if candidates else user.created_at


def _cooldown_active(db, user_id):
    cutoff = datetime.utcnow() - COOLDOWN
    return (
        db.query(ReminderEmailLog.id)
        .filter(ReminderEmailLog.user_id == user_id, ReminderEmailLog.sent_at >= cutoff)
        .first()
        is not None
    )


def _already_sent_this_streak(db, user_id, reminder_type, streak_start):
    return (
        db.query(ReminderEmailLog.id)
        .filter(
            ReminderEmailLog.user_id == user_id,
            ReminderEmailLog.reminder_type == reminder_type,
            ReminderEmailLog.sent_at >= streak_start,
        )
        .first()
        is not None
    )


def _already_sent_for_target(db, reminder_type, target_id):
    return (
        db.query(ReminderEmailLog.id)
        .filter(
            ReminderEmailLog.reminder_type == reminder_type,
            ReminderEmailLog.target_id == target_id,
        )
        .first()
        is not None
    )


def _log_sent(db, user_id, reminder_type, target_id=None):
    db.add(ReminderEmailLog(user_id=user_id, reminder_type=reminder_type, target_id=target_id))
    db.commit()


def _pick_tier(db, user, last_activity):
    inactive_for = datetime.utcnow() - last_activity

    if _cooldown_active(db, user.id):
        return None

    for reminder_type, threshold in TIME_TIERS:
        if inactive_for < threshold:
            continue
        if _already_sent_this_streak(db, user.id, reminder_type, last_activity):
            continue
        return reminder_type

    return None


def _last_score_and_weak_topic(db, user):
    last_answer = (
        db.query(Answer)
        .join(Question, Answer.question_id == Question.id)
        .join(InterviewSession, Question.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user.id)
        .order_by(Answer.created_at.desc())
        .first()
    )
    weak_topic = (
        db.query(UserTopic)
        .filter(UserTopic.user_id == user.id)
        .order_by(UserTopic.times_flagged.desc())
        .first()
    )
    if last_answer is None or weak_topic is None:
        return None
    return last_answer.score, weak_topic.topic


def _pick_feature(db, user):
    """Returns (feature_name, feature_url, used) for the Tier B email."""

    has_resume = db.query(Resume.id).filter(Resume.user_id == user.id).first() is not None
    has_analysis = db.query(ResumeAnalysis.id).filter(ResumeAnalysis.user_id == user.id).first() is not None
    has_coding = (
        db.query(Answer.id)
        .join(Question, Answer.question_id == Question.id)
        .join(InterviewSession, Question.session_id == InterviewSession.id)
        .filter(
            InterviewSession.user_id == user.id,
            Answer.code.isnot(None),
            Answer.code != "",
        )
        .first()
        is not None
    )
    # Raw InterviewSession.role string, not the RoleClassifier
    # domain - deliberately avoids a Gemini call inside a batch job.
    domain_count = (
        db.query(InterviewSession.role)
        .filter(InterviewSession.user_id == user.id)
        .distinct()
        .count()
    )
    has_multi_domain = domain_count > 1

    if not has_resume:
        return "Resume Upload", f"{FRONTEND_URL}/resume", False
    if not has_analysis:
        return "Resume Analysis", f"{FRONTEND_URL}/resume", False
    if not has_coding:
        return "a Coding Round", f"{FRONTEND_URL}/generate-interview", False
    if not has_multi_domain:
        return "a New Interview Domain", f"{FRONTEND_URL}/generate-interview", False

    last_analysis_at = (
        db.query(func.max(ResumeAnalysis.created_at))
        .filter(ResumeAnalysis.user_id == user.id)
        .scalar()
    )
    last_session_at = (
        db.query(func.max(InterviewSession.created_at))
        .filter(InterviewSession.user_id == user.id)
        .scalar()
    )
    if last_analysis_at and (not last_session_at or last_analysis_at >= last_session_at):
        return "Resume Analysis", f"{FRONTEND_URL}/resume", True
    return "Mock Interviews", f"{FRONTEND_URL}/generate-interview", True


def _progress_recap(db, user):
    session_count = (
        db.query(func.count(InterviewSession.id))
        .filter(InterviewSession.user_id == user.id)
        .scalar()
    )
    if not session_count:
        return None

    avg_score = (
        db.query(func.avg(Answer.score))
        .join(Question, Answer.question_id == Question.id)
        .join(InterviewSession, Question.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user.id)
        .scalar()
    )
    if avg_score is None:
        return None

    best_domain_row = (
        db.query(InterviewSession.role, func.avg(Answer.score).label("avg_score"))
        .join(Question, Question.session_id == InterviewSession.id)
        .join(Answer, Answer.question_id == Question.id)
        .filter(InterviewSession.user_id == user.id)
        .group_by(InterviewSession.role)
        .order_by(func.avg(Answer.score).desc())
        .first()
    )
    best_domain = best_domain_row[0] if best_domain_row else "your practiced role"

    return session_count, float(avg_score), best_domain


def _send(email_service, allowlist, recipient_email, send_fn) -> bool:
    """Returns whether the email was actually sent. Callers must
    only write a reminder_email_log row when this is True - logging
    on every match regardless of allowlist skip would falsely mark
    real users as "already reminded" for something they never
    received, silently blocking them from ever getting it."""

    if allowlist and recipient_email.lower() not in allowlist:
        print(f"  [skip-not-allowlisted] would send to {recipient_email}")
        return False
    send_fn(email_service)
    return True


def run(dry_run: bool):
    lock_conn = engine.connect()
    got_lock = lock_conn.execute(
        text("SELECT pg_try_advisory_lock(:key)"), {"key": ADVISORY_LOCK_KEY}
    ).scalar()

    if not got_lock:
        print("Another instance is already running - exiting without sending anything.")
        lock_conn.close()
        return

    try:
        _run_locked(dry_run)
    finally:
        lock_conn.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": ADVISORY_LOCK_KEY})
        lock_conn.close()


def _run_locked(dry_run: bool):
    db = SessionLocal()
    email_service = EmailService()
    allowlist = _get_allowlist()
    if allowlist:
        print(f"REMINDER_EMAIL_ALLOWLIST active: {sorted(allowlist)}")

    sent_count = 0
    error_count = 0

    try:
        users = (
            db.query(User)
            .filter((User.auth_provider != "local") | (User.email_verified.is_(True)))
            .filter(User.email_opt_out.is_(False))
            .all()
        )

        for user in users:
            try:
                last_activity = _last_activity(db, user)
                tier = _pick_tier(db, user, last_activity)

                if tier == "inactive_2d":
                    data = _last_score_and_weak_topic(db, user)
                    if data is None:
                        tier = None
                    else:
                        last_score, weak_topic = data
                        print(f"[{tier}] {user.email}: score={last_score}, weak_topic={weak_topic}")
                        if not dry_run:
                            sent = _send(
                                email_service, allowlist, user.email,
                                lambda svc: svc.send_reminder_highlight_email(
                                    recipient_email=user.email,
                                    recipient_name=user.username,
                                    last_score=last_score,
                                    weak_topic=weak_topic,
                                    unsubscribe_token=create_unsubscribe_token(user.id),
                                ),
                            )
                            if sent:
                                _log_sent(db, user.id, tier)
                        sent_count += 1

                elif tier == "inactive_4d":
                    feature_name, feature_url, used = _pick_feature(db, user)
                    print(f"[{tier}] {user.email}: feature={feature_name}, used={used}")
                    if not dry_run:
                        sent = _send(
                            email_service, allowlist, user.email,
                            lambda svc: svc.send_reminder_feature_email(
                                recipient_email=user.email,
                                recipient_name=user.username,
                                feature_name=feature_name,
                                feature_url=feature_url,
                                used=used,
                                unsubscribe_token=create_unsubscribe_token(user.id),
                            ),
                        )
                        if sent:
                            _log_sent(db, user.id, tier)
                    sent_count += 1

                elif tier == "inactive_6d":
                    recap = _progress_recap(db, user)
                    if recap is None:
                        tier = None
                    else:
                        session_count, avg_score, best_domain = recap
                        print(f"[{tier}] {user.email}: sessions={session_count}, avg={avg_score:.0f}, domain={best_domain}")
                        if not dry_run:
                            sent = _send(
                                email_service, allowlist, user.email,
                                lambda svc: svc.send_reminder_progress_recap_email(
                                    recipient_email=user.email,
                                    recipient_name=user.username,
                                    session_count=session_count,
                                    avg_score=avg_score,
                                    best_domain=best_domain,
                                    unsubscribe_token=create_unsubscribe_token(user.id),
                                ),
                            )
                            if sent:
                                _log_sent(db, user.id, tier)
                        sent_count += 1

            except Exception as error:
                error_count += 1
                print(f"  [error] tier reminder for {user.email}: {error}")

        # Event-based nudges - independent of the time-tier cooldown
        # above but still capped so a user doesn't get a tier email
        # and an event email on the same run.
        unfinished_cutoff = datetime.utcnow() - UNFINISHED_SESSION_AGE
        unfinished_sessions = (
            db.query(InterviewSession)
            .filter(
                InterviewSession.finished_at.is_(None),
                InterviewSession.created_at <= unfinished_cutoff,
            )
            .all()
        )
        for session in unfinished_sessions:
            try:
                if _already_sent_for_target(db, "unfinished_session", session.id):
                    continue
                user = db.query(User).filter(User.id == session.user_id).first()
                if user is None or user.email_opt_out or _cooldown_active(db, user.id):
                    continue
                print(f"[unfinished_session] {user.email}: session_id={session.id}, role={session.role}")
                if not dry_run:
                    sent = _send(
                        email_service, allowlist, user.email,
                        lambda svc: svc.send_unfinished_session_email(
                            recipient_email=user.email,
                            recipient_name=user.username,
                            session_id=session.id,
                            role=session.role,
                            unsubscribe_token=create_unsubscribe_token(user.id),
                        ),
                    )
                    if sent:
                        _log_sent(db, user.id, "unfinished_session", target_id=session.id)
                sent_count += 1
            except Exception as error:
                error_count += 1
                print(f"  [error] unfinished_session {session.id}: {error}")

        stalled_cutoff = datetime.utcnow() - STALLED_ANALYSIS_AGE
        stalled_analyses = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.status.in_(STALLED_ANALYSIS_STATUSES),
                ResumeAnalysis.created_at <= stalled_cutoff,
            )
            .all()
        )
        for analysis in stalled_analyses:
            try:
                if _already_sent_for_target(db, "stalled_resume_analysis", analysis.id):
                    continue
                user = db.query(User).filter(User.id == analysis.user_id).first()
                if user is None or user.email_opt_out or _cooldown_active(db, user.id):
                    continue
                job_title = analysis.job_title or "that role"
                print(f"[stalled_resume_analysis] {user.email}: analysis_id={analysis.id}, job_title={job_title}")
                if not dry_run:
                    sent = _send(
                        email_service, allowlist, user.email,
                        lambda svc: svc.send_stalled_analysis_email(
                            recipient_email=user.email,
                            recipient_name=user.username,
                            analysis_id=analysis.id,
                            job_title=job_title,
                            unsubscribe_token=create_unsubscribe_token(user.id),
                        ),
                    )
                    if sent:
                        _log_sent(db, user.id, "stalled_resume_analysis", target_id=analysis.id)
                sent_count += 1
            except Exception as error:
                error_count += 1
                print(f"  [error] stalled_analysis {analysis.id}: {error}")

    finally:
        db.close()

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n[{mode}] done. matched={sent_count} errors={error_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
