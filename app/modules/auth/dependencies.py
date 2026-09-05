"""Reusable authentication / authorization dependencies.

Every future module (Farmer, Consumer, Marketplace, ...) imports these
instead of re-implementing JWT checks or role checks:

    from app.modules.auth.dependencies import get_current_user, require_role

    @router.get("/my-farm")
    def my_farm(user: User = Depends(get_current_user)): ...

    @router.post("/admin-only")
    def admin_only(user: User = Depends(require_role(Role.ADMIN))): ...

    # Allow several roles at once:
    @router.get("/buyers")
    def buyers(user: User = Depends(require_role(Role.CONSUMER, Role.BULK_BUYER))): ...

Authorization model:
    - missing / invalid / expired JWT        -> HTTP 401
    - valid JWT but wrong role               -> HTTP 403
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.core.security import decode_access_token
from app.models.user import User

# Swagger/OpenAPI: this makes the "Authorize" button appear so protected
# endpoints can be tried from /docs. auto_error=False lets us raise a clean
# 401 ourselves when the header is missing.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Dependency that resolves the JWT to the database User (or raises 401)."""
    if credentials is None:
        raise _unauthorized("Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        # Covers malformed tokens, wrong signature AND expired tokens.
        raise _unauthorized("Invalid or expired token")

    try:
        user_id = int(payload.get("sub", ""))
    except ValueError:
        raise _unauthorized("Invalid or expired token")

    user = db.get(User, user_id)
    if user is None:
        # Token is valid but the user no longer exists.
        raise _unauthorized("User no longer exists")

    return user


def require_role(*roles: Role):
    """Build a FastAPI dependency that only allows the given role(s).

    Examples:
        require_role(Role.ADMIN)                       -> only ADMIN
        require_role(Role.FARMER)                      -> only FARMER
        require_role(Role.CONSUMER, Role.BULK_BUYER)   -> either of them
    """

    allowed_roles = {role.value for role in roles}

    def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            required = ", ".join(sorted(allowed_roles))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role {current_user.role!r} is not allowed. "
                    f"Required role(s): {required}."
                ),
            )
        return current_user

    return role_checker


def _unauthorized(detail: str) -> HTTPException:
    """401 with the WWW-Authenticate header that HTTP clients expect."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
