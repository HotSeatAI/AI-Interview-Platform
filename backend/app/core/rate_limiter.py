"""
Shared rate limiter instance (slowapi/limits).

Key function: authenticated requests are keyed by the account's email
(decoded straight from the JWT's "sub" claim, no DB lookup needed just
to bucket a rate limit), so a user's AI-cost/code-execution limits
follow them regardless of IP. Requests with no valid token (signup,
login, forgot-password, ...) fall back to the client IP - the only
identity available before authentication succeeds.
"""

from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import ALGORITHM, RATE_LIMIT_STORAGE_URI, SECRET_KEY


def rate_limit_key(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")

            if email:
                return f"user:{email}"

        except JWTError:
            pass

    return get_remote_address(request)


limiter = Limiter(
    key_func=rate_limit_key,
    storage_uri=RATE_LIMIT_STORAGE_URI,
    default_limits=["60/minute"],
    headers_enabled=True,
)
