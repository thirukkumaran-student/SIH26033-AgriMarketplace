"""Admin Verification Routes.

- GET    /api/admin/verifications              -> verification queue
- GET    /api/admin/verifications/{user_id}    -> farmer's full details
- POST   /api/admin/verifications/{user_id}/approve  -> approve
- POST   /api/admin/verifications/{user_id}/reject   -> reject (remarks required)

All routes require a valid JWT with role = ADMIN.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role, VerificationStatus
from app.models.farmer import FarmerProfile, VerificationDocument
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.admin import (
    AdminActionResponse,
    AdminFarmerProfileResponse,
    AdminRejectRequest,
    AdminVerificationDetailResponse,
    AdminVerificationDocumentResponse,
    AdminVerificationQueueItem,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])
DbSession = Annotated[Session, Depends(get_db)]


def _get_verification_user_or_404(db: Session, user_id: int) -> User:
    """Fetch a farmer or financier who has verification documents."""
    user = db.get(User, user_id)

    if user is None or user.role not in {
        Role.FARMER.value,
        Role.FINANCIER.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification user with user_id={user_id} not found",
        )

    return user


def _get_verification_documents(
    db: Session,
    user_id: int,
) -> list[VerificationDocument]:
    """Return all verification documents for a given user."""
    return list(db.scalars(
        select(VerificationDocument).where(VerificationDocument.user_id == user_id)
    ).all())


def _compute_overall_status(docs: list[VerificationDocument]) -> str:
    """Compute overall status from a list of documents."""
    if not docs:
        return VerificationStatus.PENDING.value
    statuses = {d.status for d in docs}
    if VerificationStatus.PENDING.value in statuses:
        return VerificationStatus.PENDING.value
    if all(d.status == VerificationStatus.APPROVED.value for d in docs):
        return VerificationStatus.APPROVED.value
    return VerificationStatus.REJECTED.value


# ---------------------------------------------------------------------------
# GET /api/admin/verifications  —  verification queue
# ---------------------------------------------------------------------------


@router.get(
    "/verifications",
    response_model=list[AdminVerificationQueueItem],
    summary="Get verification queue",
)
def list_verifications(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> list[AdminVerificationQueueItem]:
    """Return all farmers who have submitted verification documents.

    Results are grouped by farmer, ordered by earliest submission.
    """
    # Sub-query: find all distinct user_ids that have at least one document
    subq = (
        select(
            VerificationDocument.user_id,
            func.min(VerificationDocument.submitted_at).label("earliest_submission"),
            func.count(VerificationDocument.id).label("document_count"),
        )
        .group_by(VerificationDocument.user_id)
        .subquery()
    )

    rows = db.execute(select(subq)).all()

    result: list[AdminVerificationQueueItem] = []
    for row in rows:
        user = db.get(User, row.user_id)
        if user is None:
            continue
        docs = _get_verification_documents(db, row.user_id)
        overall = _compute_overall_status(docs)
        result.append(
            AdminVerificationQueueItem(
                user_id=row.user_id,
                applicant_name=user.name,
                farmer_email=user.email,
                overall_status=overall,
                document_count=row.document_count,
                earliest_submission=row.earliest_submission,
            )
        )

    # Sort by earliest_submission ascending (oldest first)
    result.sort(key=lambda x: x.earliest_submission)
    return result


# ---------------------------------------------------------------------------
# GET /api/admin/verifications/{user_id}  —  full detail view
# ---------------------------------------------------------------------------


@router.get(
    "/verifications/{user_id}",
    response_model=AdminVerificationDetailResponse,
    summary="View a farmer's verification details",
)
def get_farmer_verification(
    user_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> AdminVerificationDetailResponse:
    """Return the farmer's profile + all verification documents for review."""
    verification_user = _get_verification_user_or_404(db, user_id)
    docs = _get_verification_documents(db, user_id)

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification documents found for farmer user_id={user_id}",
        )

    profile = db.scalar(
        select(FarmerProfile).where(FarmerProfile.user_id == user_id)
    )

    return AdminVerificationDetailResponse(
        user_id=verification_user.id,
        applicant_name=verification_user.name,
        farmer_email=verification_user.email,
        overall_status=_compute_overall_status(docs),
        profile=AdminFarmerProfileResponse.model_validate(profile) if profile else None,
        documents=[AdminVerificationDocumentResponse.model_validate(d) for d in docs],
    )


# ---------------------------------------------------------------------------
# POST /api/admin/verifications/{user_id}/approve
# ---------------------------------------------------------------------------


@router.post(
    "/verifications/{user_id}/approve",
    response_model=AdminActionResponse,
    summary="Approve a farmer's verification",
)
def approve_farmer(
    user_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> AdminActionResponse:
    """Set all PENDING documents for the farmer to APPROVED."""
    verification_user = _get_verification_user_or_404(db, user_id)
    docs = _get_verification_documents(db, user_id)

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification documents found for farmer user_id={user_id}",
        )

    now = datetime.now(timezone.utc)
    updated = 0
    for doc in docs:
        if doc.status != VerificationStatus.APPROVED.value:
            doc.status = VerificationStatus.APPROVED.value
            doc.reviewed_by = current_user.id
            doc.reviewed_at = now
            updated += 1

    db.commit()

    return AdminActionResponse(
        user_id=verification_user.id,
        applicant_name=verification_user.name,
        action="APPROVE",
        new_status=VerificationStatus.APPROVED,
        reviewed_by=current_user.id,
        reviewed_at=now,
        documents_updated=updated,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/verifications/{user_id}/reject
# ---------------------------------------------------------------------------


@router.post(
    "/verifications/{user_id}/reject",
    response_model=AdminActionResponse,
    summary="Reject a farmer's verification",
)
def reject_farmer(
    user_id: int,
    payload: AdminRejectRequest,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> AdminActionResponse:
    """Set all PENDING documents for the farmer to REJECTED with remarks."""
    verification_user = _get_verification_user_or_404(db, user_id)
    docs = _get_verification_documents(db, user_id)

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification documents found for farmer user_id={user_id}",
        )

    now = datetime.now(timezone.utc)
    updated = 0
    for doc in docs:
        if doc.status != VerificationStatus.REJECTED.value:
            doc.status = VerificationStatus.REJECTED.value
            doc.remarks = payload.remarks
            doc.reviewed_by = current_user.id
            doc.reviewed_at = now
            updated += 1

    db.commit()

    return AdminActionResponse(
        user_id=verification_user.id,
        applicant_name=verification_user.name,
        action="REJECT",
        new_status=VerificationStatus.REJECTED,
        reviewed_by=current_user.id,
        reviewed_at=now,
        documents_updated=updated,
        remarks=payload.remarks,
    )
