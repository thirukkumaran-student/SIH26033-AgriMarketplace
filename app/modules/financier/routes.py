from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.financier import FinancierProfile
from app.core.enums import Role, VerificationStatus
from app.models.user import User
from app.modules.auth.dependencies import require_role
from app.core.enums import Role
from app.schemas.financier import (
    FinancierProfileCreate,
    FinancierProfileResponse,
    FinancierProfileUpdate,
)
from app.models.farmer import VerificationDocument
from app.models.financier import FinancierProfile
from app.models.user import User

router = APIRouter(
    prefix="/api/financier",
    tags=["Financier"],
)


@router.post(
    "/profile",
    response_model=FinancierProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    data: FinancierProfileCreate,
    current_user: Annotated[
        User,
        Depends(require_role(Role.FINANCIER)),
    ],
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(FinancierProfile).where(
            FinancierProfile.user_id == current_user.id
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Financier profile already exists",
        )

    profile = FinancierProfile(
        user_id=current_user.id,
        **data.model_dump(),
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get(
    "/profile",
    response_model=FinancierProfileResponse,
)
def get_profile(
    current_user: Annotated[
        User,
        Depends(require_role(Role.FINANCIER)),
    ],
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(FinancierProfile).where(
            FinancierProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financier profile not found",
        )

    return profile


@router.put(
    "/profile",
    response_model=FinancierProfileResponse,
)
def update_profile(
    data: FinancierProfileUpdate,
    current_user: Annotated[
        User,
        Depends(require_role(Role.FINANCIER)),
    ],
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(FinancierProfile).where(
            FinancierProfile.user_id == current_user.id
        )
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financier profile not found",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile

@router.get(
    "/",
    response_model=list[FinancierProfileResponse],
    summary="List eligible financiers",
)
def list_financiers(
    current_user: Annotated[
        User,
        Depends(require_role(Role.BULK_BUYER)),
    ],
    db: Session = Depends(get_db),
) -> list[FinancierProfile]:
    """Return financiers whose verification has been approved."""

    financiers = db.scalars(
        select(FinancierProfile)
        .join(User, FinancierProfile.user_id == User.id)
        .where(User.role == Role.FINANCIER.value)
    ).all()

    eligible = []

    for financier in financiers:
        docs = db.scalars(
            select(VerificationDocument).where(
                VerificationDocument.user_id == financier.user_id
            )
        ).all()

        if docs and all(
            doc.status == VerificationStatus.APPROVED.value
            for doc in docs
        ):
            eligible.append(financier)

    return list(eligible)