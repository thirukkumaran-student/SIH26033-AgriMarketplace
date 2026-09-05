"""Password hashing and JWT helpers.

Note on libraries: we use the ``bcrypt`` package directly instead of
``passlib``. passlib is unmaintained and breaks with bcrypt >= 4.1
(``AttributeError: module 'bcrypt' has no attribute '__about__'``), which is
what a fresh install of bcrypt today provides. The bcrypt package itself is
maintained and exposes simple ``hashpw`` / ``checkpw`` functions.

Never log passwords or password hashes anywhere in this app.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt and return the stored string."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        # bcrypt only uses the first 72 bytes of the password.
        raise ValueError("Password must be at most 72 bytes long for bcrypt.")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        # Malformed hash / password that can't be checked -> treat as invalid.
        return False


# ---------------------------------------------------------------------------
# JWT (JSON Web Tokens)
# ---------------------------------------------------------------------------


def create_access_token(
    *,
    subject: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT containing the user's identity (``sub``) and role.

    ``expires_delta`` overrides the default lifetime from configuration
    (used mainly by tests to forge already-expired tokens).
    """
    now = datetime.now(timezone.utc)
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": subject,            # user id (string, as required by the JWT spec)
        "role": role,              # one of app.core.enums.Role values
        "iat": now,                # issued at
        "exp": now + expires_delta,  # expires at
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate ``token`` (signature, expiry, algorithm) and return its claims.

    Raises a ``jwt.InvalidTokenError`` subclass when the token is malformed,
    has a bad signature, or is expired. Callers decide how to handle that
    (the auth dependency turns it into an HTTP 401).
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
