from fastapi import Depends, HTTPException

from app.api.auth import get_current_user
from app.models.user import User


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Same login/JWT as every other user - admin is just a role
    flag on the existing User row, not a separate auth system.
    Use as a route dependency to gate admin-only endpoints.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required.",
        )

    return current_user
