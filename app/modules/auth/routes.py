"""Routes for the shared authentication module.

- POST /api/auth/register   -> create a user (any supported role)
- POST /api/auth/login      -> verify credentials, return a JWT
- GET  /api/auth/me         -> current user (requires JWT)
- GET  /api/auth/test-farmer / test-admin -> temporary RBAC demo endpoints

Identifiers are role-specific:
- FARMER  -> phone + password
- other roles -> email + password

The login flow never reveals whether the identifier or the password was
wrong: both failures produce the exact same error response.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.user import LoginRequest, TokenResponse, UserPublic, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


def _is_email_like(identifier: str) -> bool:
    """Return True when the identifier looks like an email address."""
    return "@" in identifier


def _find_user_by_identifier(db: Session, identifier: str) -> User | None:
    """Resolve an identifier to a user using the identifier's format.

    Email-like identifiers are matched against ``users.email``; anything else
    (a phone number) is normalized and matched against ``users.phone``.
    Malformed phone identifiers simply resolve to no user.
    """
    if _is_email_like(identifier):
        return db.scalar(select(User).where(User.email == identifier.strip().lower()))
    try:
        from app.schemas.user import normalize_phone

        phone = normalize_phone(identifier)
    except ValueError:
        return None
    return db.scalar(select(User).where(User.phone == phone))


def _identifier_matches_role(user: User, identifier: str) -> bool:
    """Enforce the role-specific login identifier contract.

    FARMER must authenticate with a phone number; every other role must
    authenticate with an email address.
    """
    if user.role == Role.FARMER.value:
        return not _is_email_like(identifier)
    return _is_email_like(identifier)


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: UserRegister, db: DbSession) -> User:
    """Create a user for any supported role.

    FARMER: phone required (email optional). Others: email required.
    Both identifiers are normalized and unique when present.
    """
    email = payload.email  # already lowercased/trimmed by the schema validator
    phone = payload.phone  # already normalized by the schema validator

    if email is not None:
        existing = db.scalar(select(User).where(User.email == email))
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered",
            )

    if phone is not None:
        existing = db.scalar(select(User).where(User.phone == phone))
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This phone number is already registered",
            )

    user = User(
        name=payload.name,
        email=email,
        phone=phone,
        role=payload.role.value,  # store the enum value ("FARMER", ...)
        password_hash=hash_password(payload.password),  # never store plaintext
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # Race condition: another request registered the same identifier first.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Identifier is already registered",
        )

    db.refresh(user)  # load the DB-generated created_at
    return user  # password_hash is excluded by the response schema


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with identifier and password, returns a JWT",
)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    """Verify credentials and return an access token + safe user info.

    The identifier is a phone number for FARMER accounts and an email for
    every other role; the format determines which lookup is used.
    """
    user = _find_user_by_identifier(db, payload.identifier)

    # One generic message for "unknown identifier", "wrong identifier type",
    # AND "wrong password" so the endpoint does not reveal which caused it.
    if (
        user is None
        or not _identifier_matches_role(user, payload.identifier)
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id), role=user.role)

    return TokenResponse(access_token=access_token, user=UserPublic.model_validate(user))


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get the current authenticated user",
)
def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Requires a valid JWT. Never returns the password hash."""
    return current_user


# ---------------------------------------------------------------------------
# TEMPORARY endpoints that only exist to demonstrate RBAC. They are clearly
# marked and should be removed once the real feature modules are built.
# ---------------------------------------------------------------------------

TEST_ENDPOINTS_DESCRIPTION = (
    "TEMPORARY development endpoint used to demonstrate role-based access "
    "control (RBAC). It will be removed once the real feature modules exist."
)


@router.get(
    "/test-farmer",
    summary="[DEV/TEST] Only FARMER can access",
    description=TEST_ENDPOINTS_DESCRIPTION,
)
def test_farmer(
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> dict:
    return {"message": "FARMER access granted", "user_id": current_user.id}


@router.get(
    "/test-admin",
    summary="[DEV/TEST] Only ADMIN can access",
    description=TEST_ENDPOINTS_DESCRIPTION,
)
def test_admin(
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> dict:
    return {"message": "ADMIN access granted", "user_id": current_user.id}
