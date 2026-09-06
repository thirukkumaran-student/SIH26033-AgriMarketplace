"""Routes for Consumer Profile.

- POST   /api/consumer/profile  -> create profile (one per consumer)
- GET    /api/consumer/profile  -> view own profile
- PUT    /api/consumer/profile  -> update own profile

All routes require a valid JWT with role = CONSUMER.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.consumer import ConsumerProfile
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.consumer import (
    ConsumerProfileCreate,
    ConsumerProfileResponse,
    ConsumerProfileUpdate,
)

router = APIRouter(prefix="/api/consumer", tags=["consumer"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/profile",
    response_model=ConsumerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create the consumer's profile",
)
def create_profile(
    payload: ConsumerProfileCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> ConsumerProfile:
    """Create a consumer profile. Only one profile per consumer — duplicate creation returns 409."""
    existing = db.scalar(
        select(ConsumerProfile).where(ConsumerProfile.user_id == current_user.id)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A consumer profile already exists for this user",
        )

    profile = ConsumerProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get(
    "/profile",
    response_model=ConsumerProfileResponse,
    summary="Get own consumer profile",
)
def read_profile(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> ConsumerProfile:
    """Return the authenticated consumer's profile. 404 if none exists yet."""
    profile = db.scalar(
        select(ConsumerProfile).where(ConsumerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer profile not found. Create one with POST /api/consumer/profile",
        )
    return profile


@router.put(
    "/profile",
    response_model=ConsumerProfileResponse,
    summary="Update own consumer profile",
)
def update_profile(
    payload: ConsumerProfileUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> ConsumerProfile:
    """Update the authenticated consumer's profile. 404 if none exists."""
    profile = db.scalar(
        select(ConsumerProfile).where(ConsumerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer profile not found. Create one with POST /api/consumer/profile",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields to update",
        )
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
