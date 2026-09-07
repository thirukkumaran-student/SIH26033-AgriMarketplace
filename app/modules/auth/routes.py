"""Routes for the shared authentication module.

- POST /api/auth/register   -> create a user (any supported role)
- POST /api/auth/login      -> verify credentials, return a JWT
- GET  /api/auth/me         -> current user (requires JWT)
- GET  /api/auth/test-farmer / test-admin -> temporary RBAC demo endpoints

The login flow never reveals whether the email or the password was wrong:
both failures produce the exact same error response.
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


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: UserRegister, db: DbSession) -> User:
    """Create a user for any supported role. Email is normalized + unique."""
    email = payload.email  # already lowercased/trimmed by the schema validator

    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        name=payload.name,
        email=email,
        role=payload.role.value,  # store the enum value ("FARMER", ...)
        password_hash=hash_password(payload.password),  # never store plaintext
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # Race condition: another request registered the same email first.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    db.refresh(user)  # load the DB-generated created_at
    return user  # password_hash is excluded by the response schema


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password, returns a JWT",
)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    """Verify credentials and return an access token + safe user info."""
    user = db.scalar(select(User).where(User.email == payload.email))

    # One generic message for "unknown email" AND "wrong password" so the
    # endpoint does not reveal which one caused the failure.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
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