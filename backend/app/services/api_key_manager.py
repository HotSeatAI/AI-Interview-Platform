import contextlib
import contextvars
import threading
import time

from google import genai
from google.genai.errors import APIError

from app.core.config import (
    GEMINI_API_KEYS,
    GEMINI_MODEL,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
)

# ============================================================
# LangFuse tracing (optional)
#
# Disabled unless both LangFuse keys are configured, so local
# dev / deployments without a LangFuse project keep working
# exactly as before. When enabled, every Gemini call made
# through this manager is auto-captured (prompt, response,
# tokens, latency) via OpenInference's google-genai
# instrumentation, tagged with the call's `purpose` and the
# owning resume-analysis id (when set).
# ============================================================

LANGFUSE_ENABLED = bool(
    LANGFUSE_PUBLIC_KEY
    and LANGFUSE_SECRET_KEY
)

if LANGFUSE_ENABLED:

    from openinference.instrumentation.google_genai import (
        GoogleGenAIInstrumentor,
    )
    from langfuse import (
        get_client as get_langfuse_client,
        propagate_attributes,
    )

    GoogleGenAIInstrumentor().instrument()

    get_langfuse_client()


# ============================================================
# Per-analysis Gemini call telemetry
#
# Lets the resume-analysis worker tag every Gemini call with
# the analysis it belongs to and count calls per analysis,
# WITHOUT threading an analysis_id parameter through every
# service function. Never logs prompt content or API keys.
# ============================================================

_analysis_id_var: contextvars.ContextVar = contextvars.ContextVar(
    "gemini_analysis_id",
    default=None,
)

_call_count_var: contextvars.ContextVar = contextvars.ContextVar(
    "gemini_call_count",
    default=0,
)


def set_gemini_context(analysis_id) -> None:
    """
    Associate all subsequent Gemini calls made on this thread
    with the given analysis id, and reset the call counter.
    """

    _analysis_id_var.set(analysis_id)
    _call_count_var.set(0)


def clear_gemini_context() -> None:

    _analysis_id_var.set(None)
    _call_count_var.set(0)


def get_gemini_call_count() -> int:

    return _call_count_var.get()


class APIKeyManager:
    """
    Centralized Gemini API key manager.

    Responsibilities:
    - Maintain multiple Gemini API keys.
    - Rotate to the next key instantly when Gemini returns 429
      (quota) or a 404 caused by the current key lacking access
      to the configured model, and retry the same in-flight
      request on the new key.
    - Retry with bounded exponential backoff when Gemini
      returns 503 (model temporarily unavailable/overloaded).
    - Let a key marked exhausted become eligible again after a
      cooldown, since Gemini quotas reset per-minute.
    - Support both simple prompts and structured
      google-genai requests.
    - Share the same rotation state across the application.
    - Log per-analysis Gemini call telemetry (call number,
      purpose, model, success/failure) without ever logging
      API keys or raw prompt/response content.

    The manager does NOT make decisions about prompts,
    schemas, or application logic. It only manages
    Gemini API access.
    """

    # Bounded retry behavior for transient 503 errors.
    # This is intentionally small — a persistent outage
    # should surface as a clear failure, not retry forever.
    MAX_UNAVAILABLE_RETRIES = 3
    BASE_BACKOFF_SECONDS = 1.0
    MAX_BACKOFF_SECONDS = 8.0

    # How long a key stays skipped after being marked exhausted
    # (rate-limited or found to lack model access). Gemini quotas
    # are per-minute, so a key that looked exhausted a minute ago
    # is very likely usable again — without this, exhausted_keys
    # only ever grows and the whole pool eventually looks dead for
    # the lifetime of the process.
    EXHAUSTION_COOLDOWN_SECONDS = 60

    def __init__(self):

        self.api_keys = list(
            dict.fromkeys(
                GEMINI_API_KEYS
            )
        )

        if not self.api_keys:
            raise ValueError(
                "No Gemini API keys found. "
                "Please configure GEMINI_API_KEYS "
                "in your .env file."
            )

        self.current_index = 0

        # index -> timestamp (time.time()) it was marked exhausted
        self.exhausted_keys = {}

        self.lock = threading.Lock()

    # ========================================================
    # Client handling
    # ========================================================

    def _get_client(self):
        """
        Return a Gemini client for the currently
        active API key.
        """

        with self.lock:

            api_key = self.api_keys[
                self.current_index
            ]

        return genai.Client(
            api_key=api_key,
        )

    # ========================================================
    # Key rotation
    # ========================================================

    def _move_to_next_key(self):
        """
        Mark the current key as exhausted and
        instantly move to the next available key.

        A key marked exhausted is only skipped for
        EXHAUSTION_COOLDOWN_SECONDS — after that it is treated as
        available again, since Gemini quotas reset per-minute and
        a permanently-blacklisted key would otherwise shrink the
        usable pool to nothing over the life of the process.
        """

        with self.lock:

            now = time.time()

            exhausted_index = (
                self.current_index
            )

            self.exhausted_keys[exhausted_index] = now

            for index in range(
                len(self.api_keys)
            ):

                exhausted_at = self.exhausted_keys.get(index)

                if (
                    exhausted_at is not None
                    and (now - exhausted_at)
                    < self.EXHAUSTION_COOLDOWN_SECONDS
                ):
                    continue

                self.current_index = index

                print(
                    "\n[Gemini API] "
                    f"Switched to API Key #{index + 1}"
                )

                return

        raise RuntimeError(
            "All configured Gemini API keys "
            "have exhausted their available quota."
        )

    # ========================================================
    # Telemetry
    # ========================================================

    def _log_call_start(
        self,
        purpose: str,
        model: str,
    ) -> tuple[int, object]:

        analysis_id = _analysis_id_var.get()

        call_number = (
            _call_count_var.get()
            + 1
        )

        _call_count_var.set(
            call_number
        )

        label = (
            f"[ResumeAnalysis {analysis_id}]"
            if analysis_id is not None
            else "[Gemini]"
        )

        print(
            f"{label} Gemini Call {call_number} "
            f"-> {purpose} (model={model})"
        )

        return call_number, analysis_id

    @staticmethod
    def _log_call_result(
        analysis_id,
        call_number: int,
        purpose: str,
        outcome: str,
    ) -> None:

        label = (
            f"[ResumeAnalysis {analysis_id}]"
            if analysis_id is not None
            else "[Gemini]"
        )

        print(
            f"{label} Gemini Call {call_number} "
            f"({purpose}) -> {outcome}"
        )

    # ========================================================
    # Gemini generation
    # ========================================================

    def generate_content(
        self,
        prompt=None,
        *,
        contents=None,
        config=None,
        model=None,
        purpose="unspecified",
    ):
        """
        Generate Gemini content.

        Backwards compatible with the existing usage:

            manager.generate_content(
                prompt="..."
            )

        Also supports the newer google-genai API:

            manager.generate_content(
                contents=prompt,
                config=...
            )

        This is important because resume analysis uses
        structured JSON responses.

        `purpose` is a short human-readable label used only
        for telemetry (e.g. "jd_structuring",
        "batched_recommendations") — it never affects the
        request sent to Gemini.
        """

        if contents is None:

            if prompt is None:
                raise ValueError(
                    "Either 'prompt' or 'contents' "
                    "must be provided."
                )

            contents = prompt

        model = (
            model
            or GEMINI_MODEL
        )

        call_number, analysis_id = (
            self._log_call_start(
                purpose,
                model,
            )
        )

        unavailable_attempts = 0

        while True:

            client = self._get_client()

            trace_scope = (
                propagate_attributes(
                    session_id=(
                        str(analysis_id)
                        if analysis_id is not None
                        else None
                    ),
                    metadata={"purpose": purpose},
                    tags=[purpose],
                )
                if LANGFUSE_ENABLED
                else contextlib.nullcontext()
            )

            try:

                with trace_scope:

                    if config is None:

                        response = (
                            client.models.generate_content(
                                model=model,
                                contents=contents,
                            )
                        )

                    else:

                        response = (
                            client.models.generate_content(
                                model=model,
                                contents=contents,
                                config=config,
                            )
                        )

                self._log_call_result(
                    analysis_id,
                    call_number,
                    purpose,
                    "success",
                )

                return response

            except APIError as error:

                if self._is_rate_limit_error(
                    error
                ):

                    current_key_number = (
                        self.current_index + 1
                    )

                    print(
                        "\n[Gemini API] "
                        f"API Key #{current_key_number} "
                        "received a 429 response."
                    )

                    try:
                        self._move_to_next_key()

                    except RuntimeError:

                        self._log_call_result(
                            analysis_id,
                            call_number,
                            purpose,
                            "failed (all API keys rate-limited)",
                        )

                        raise

                    continue

                if self._is_key_access_error(
                    error
                ):

                    current_key_number = (
                        self.current_index + 1
                    )

                    print(
                        "\n[Gemini API] "
                        f"API Key #{current_key_number} "
                        "does not have access to this model "
                        "(404). Rotating keys."
                    )

                    try:
                        self._move_to_next_key()

                    except RuntimeError:

                        self._log_call_result(
                            analysis_id,
                            call_number,
                            purpose,
                            "failed (no configured key has model access)",
                        )

                        raise

                    continue

                if self._is_unavailable_error(
                    error
                ):

                    unavailable_attempts += 1

                    if (
                        unavailable_attempts
                        > self.MAX_UNAVAILABLE_RETRIES
                    ):

                        # Local backoff on this key is exhausted.
                        # A "503 unavailable" response isn't
                        # always a genuine model-wide outage —
                        # some quota-exhaustion errors (e.g. a
                        # free-tier key that has used its full
                        # daily request allowance) can surface
                        # through this SDK in the same 503 shape
                        # rather than as a standard 429. Rather
                        # than failing immediately, try rotating
                        # to another configured key and giving
                        # the request a fresh attempt there —
                        # this only costs extra time if the
                        # outage really is model-wide, but
                        # recovers the analysis if it was
                        # actually a per-key quota problem.

                        current_key_number = (
                            self.current_index + 1
                        )

                        print(
                            "\n[Gemini API] "
                            f"API Key #{current_key_number} "
                            "exhausted its 503 retry budget. "
                            "Trying next key."
                        )

                        try:
                            self._move_to_next_key()

                        except RuntimeError:

                            self._log_call_result(
                                analysis_id,
                                call_number,
                                purpose,
                                "failed (503 retries exhausted "
                                "on all keys)",
                            )

                            raise

                        unavailable_attempts = 0

                        continue

                    delay = min(
                        self.BASE_BACKOFF_SECONDS
                        * (2 ** (unavailable_attempts - 1)),
                        self.MAX_BACKOFF_SECONDS,
                    )

                    print(
                        "\n[Gemini API] "
                        "Model temporarily unavailable (503). "
                        f"Retrying in {delay:.1f}s "
                        f"(attempt {unavailable_attempts}/"
                        f"{self.MAX_UNAVAILABLE_RETRIES})."
                    )

                    time.sleep(delay)

                    continue

                self._log_call_result(
                    analysis_id,
                    call_number,
                    purpose,
                    f"failed ({type(error).__name__})",
                )

                raise

            except Exception as error:

                self._log_call_result(
                    analysis_id,
                    call_number,
                    purpose,
                    f"failed ({type(error).__name__})",
                )

                raise

    # ========================================================
    # Rate-limit detection
    # ========================================================

    @staticmethod
    def _is_rate_limit_error(
        error,
    ):
        """
        Detect Gemini rate-limit/quota errors.

        The google-genai SDK can expose the status
        differently depending on version, so we
        check both the explicit status and the
        error message.
        """

        status_code = getattr(
            error,
            "status_code",
            None,
        )

        if status_code == 429:
            return True

        code = getattr(
            error,
            "code",
            None,
        )

        if code == 429:
            return True

        message = str(
            error
        ).lower()

        return any(
            phrase in message
            for phrase in (
                "429",
                "resource exhausted",
                "rate limit",
                "quota exceeded",
                "quota",
                "too many requests",
            )
        )

    # ========================================================
    # Key-access detection (404 / model not available to this key)
    # ========================================================

    @staticmethod
    def _is_key_access_error(
        error,
    ):
        """
        Detect a 404 caused by the *current key's* project not
        having access to the configured model — this is a
        per-key provisioning problem, not a bad request, so it
        should trigger rotation to the next key exactly like a
        429 does, rather than being re-raised immediately.

        Deliberately narrow (status 404 + a model/access-shaped
        message) rather than "any 404", so a genuinely malformed
        request still fails fast instead of being retried against
        every configured key.
        """

        status_code = getattr(
            error,
            "status_code",
            None,
        )

        code = getattr(
            error,
            "code",
            None,
        )

        if status_code != 404 and code != 404:
            return False

        message = str(
            error
        ).lower()

        return any(
            phrase in message
            for phrase in (
                "not found for api version",
                "not supported for generatecontent",
                "is not found",
                "does not have access",
                "permission",
            )
        )

    # ========================================================
    # Availability detection (503 / model overloaded)
    # ========================================================

    @staticmethod
    def _is_unavailable_error(
        error,
    ):
        """
        Detect transient "model unavailable / overloaded"
        errors so they can be retried with bounded backoff,
        separately from rate-limit (429) handling.
        """

        status_code = getattr(
            error,
            "status_code",
            None,
        )

        if status_code == 503:
            return True

        code = getattr(
            error,
            "code",
            None,
        )

        if code == 503:
            return True

        message = str(
            error
        ).lower()

        return any(
            phrase in message
            for phrase in (
                "503",
                "unavailable",
                "overloaded",
                "high demand",
            )
        )

    # ========================================================
    # Client access
    # ========================================================

    def get_client(self):
        """
        Return a Gemini client using the currently
        active API key.

        Use generate_content() whenever possible so
        automatic key rotation is preserved.
        """

        return self._get_client()


# ============================================================
# Shared application-level manager
# ============================================================

api_key_manager = APIKeyManager()
