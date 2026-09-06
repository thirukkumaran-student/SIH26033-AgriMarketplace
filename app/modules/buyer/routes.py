"""Routes for Bulk Buyer Profile."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.buyer import BuyerProfile
from app.models.user import User
from app.modules.auth.dependencies import require_role
from app.schemas.buyer import (
    BuyerProfileCreate,
    BuyerProfileResponse,
    BuyerProfileUpdate,
)

router = APIRouter(prefix="/api/buyer", tags=["buyer"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/profile",
    response_model=BuyerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create the bulk buyer's profile",
)
def create_profile(
    payload: BuyerProfileCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.BULK_BUYER))],
) -> BuyerProfile:
    """Create one profile for the authenticated bulk buyer."""
    existing = db.scalar(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A buyer profile already exists for this user",
        )

    profile = BuyerProfile(
        user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get(
    "/profile",
    response_model=BuyerProfileResponse,
    summary="Get own bulk buyer profile",
)
def read_profile(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.BULK_BUYER))],
) -> BuyerProfile:
    """Return the authenticated bulk buyer's profile."""
    profile = db.scalar(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer profile not found. Create one with POST /api/buyer/profile",
        )
    return profile


@router.put(
    "/profile",
    response_model=BuyerProfileResponse,
    summary="Update own bulk buyer profile",
)
def update_profile(
    payload: BuyerProfileUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.BULK_BUYER))],
) -> BuyerProfile:
    """Update the authenticated bulk buyer's profile."""
    profile = db.scalar(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer profile not found. Create one with POST /api/buyer/profile",
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