"""Routes for Farmer Profile and Farmer Verification.

Farmer Profile
--------------
- POST   /api/farmer/profile      -> create profile (one per farmer)
- GET    /api/farmer/profile      -> view own profile
- PUT    /api/farmer/profile      -> update own profile

Farmer Verification
-------------------
- POST   /api/verification/documents -> submit a verification document
- GET    /api/verification/status     -> view own verification status

All routes require a valid JWT with role = FARMER.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role, VerificationStatus
from app.models.farmer import FarmerProfile, VerificationDocument
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.farmer import (
    FarmerProfileCreate,
    FarmerProfileResponse,
    FarmerProfileUpdate,
    VerificationDocumentResponse,
    VerificationDocumentSubmit,
    VerificationStatusResponse,
)

# ---------------------------------------------------------------------------
# Profile router  –  /api/farmer
# ---------------------------------------------------------------------------
profile_router = APIRouter(prefix="/api/farmer", tags=["farmer"])
DbSession = Annotated[Session, Depends(get_db)]


@profile_router.post(
    "/profile",
    response_model=FarmerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create the farmer's profile",
)
def create_profile(
    payload: FarmerProfileCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> FarmerProfile:
    """Create a farmer profile.  Only one profile per farmer — duplicate creation returns 409."""
    existing = db.scalar(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A farmer profile already exists for this user",
        )

    profile = FarmerProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@profile_router.get(
    "/profile",
    response_model=FarmerProfileResponse,
    summary="Get own farmer profile",
)
def read_profile(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> FarmerProfile:
    """Return the authenticated farmer's profile.  404 if none exists yet."""
    profile = db.scalar(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Create one with POST /api/farmer/profile",
        )
    return profile


@profile_router.put(
    "/profile",
    response_model=FarmerProfileResponse,
    summary="Update own farmer profile",
)
def update_profile(
    payload: FarmerProfileUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> FarmerProfile:
    """Update the authenticated farmer's profile.  404 if none exists."""
    profile = db.scalar(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Create one with POST /api/farmer/profile",
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


# ---------------------------------------------------------------------------
# Verification router  –  /api/verification
# ---------------------------------------------------------------------------
verification_router = APIRouter(prefix="/api/verification", tags=["verification"])


@verification_router.post(
    "/documents",
    response_model=VerificationDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a verification document",
)
def submit_document(
    payload: VerificationDocumentSubmit,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> VerificationDocument:
    """Submit a document for farmer verification.

    Each submission creates a new PENDING record.  The farmer may submit
    multiple documents of different types.
    """
    doc = VerificationDocument(
        user_id=current_user.id,
        document_type=payload.document_type.upper(),
        document_number=payload.document_number,
        file_url=payload.file_url,
        status=VerificationStatus.PENDING.value,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@verification_router.get(
    "/status",
    response_model=VerificationStatusResponse,
    summary="Get verification status",
)
def get_verification_status(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> VerificationStatusResponse:
    """Return all documents submitted by the farmer and overall status.

    Overall status logic:
    - PENDING  : at least one document is PENDING
    - APPROVED : ALL documents are APPROVED
    - REJECTED : at least one document is REJECTED (and none PENDING)
    """
    docs = db.scalars(
        select(VerificationDocument).where(VerificationDocument.user_id == current_user.id)
    ).all()

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification documents found. Submit one with POST /api/verification/documents",
        )

    doc_responses = [VerificationDocumentResponse.model_validate(d) for d in docs]
    statuses = {d.status for d in docs}

    if VerificationStatus.PENDING.value in statuses:
        overall = VerificationStatus.PENDING.value
    elif all(d.status == VerificationStatus.APPROVED.value for d in docs):
        overall = VerificationStatus.APPROVED.value
    else:
        overall = VerificationStatus.REJECTED.value

    return VerificationStatusResponse(
        farmer_name=current_user.name,
        user_id=current_user.id,
        documents=doc_responses,
        overall_status=overall,
    )
