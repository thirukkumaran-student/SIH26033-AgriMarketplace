"""Marketplace Integration Routes.

Consumer-facing READ layer over the existing Produce table.

- GET /api/marketplace/produce               -> list marketplace-eligible produce
- GET /api/marketplace/produce/{produce_id}  -> marketplace-eligible detail

Marketplace eligibility:
- Produce belongs to an APPROVED farmer
- Produce status is ACTIVE
- Produce quantity is greater than 0

This module reuses the existing Produce model. It does NOT create any duplicate
product/listing table.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import ProduceStatus, Role, VerificationStatus
from app.models.farmer import VerificationDocument
from app.models.produce import Produce
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.consumer import MarketplaceProduceResponse

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])
DbSession = Annotated[Session, Depends(get_db)]


def _get_farmer_verification_status(db: Session, farmer_id: int) -> str:
    """Return overall verification status for a farmer using the same logic as
    the existing verification/status endpoint."""
    docs = list(db.scalars(
        select(VerificationDocument).where(VerificationDocument.user_id == farmer_id)
    ).all())

    if not docs:
        return "UNVERIFIED"

    statuses = {d.status for d in docs}
    if VerificationStatus.PENDING.value in statuses:
        return VerificationStatus.PENDING.value
    if all(d.status == VerificationStatus.APPROVED.value for d in docs):
        return VerificationStatus.APPROVED.value
    return VerificationStatus.REJECTED.value


def _is_marketplace_eligible(db: Session, produce: Produce) -> bool:
    """Return True if this Produce is eligible to appear in the marketplace."""
    if produce.status != ProduceStatus.ACTIVE.value:
        return False
    if produce.quantity <= 0:
        return False
    if _get_farmer_verification_status(db, produce.farmer_id) != VerificationStatus.APPROVED.value:
        return False
    return True


@router.get(
    "/produce",
    response_model=list[MarketplaceProduceResponse],
    summary="List marketplace-eligible produce",
)
def list_marketplace_produce(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
    crop: str | None = Query(default=None, description="Filter by crop name"),
    location: str | None = Query(default=None, description="Filter by location"),
    max_price: float | None = Query(default=None, ge=0, description="Maximum price per unit"),
) -> list[MarketplaceProduceResponse]:
    """Return only marketplace-eligible produce for the authenticated CONSUMER.

    Eligibility is enforced server-side:
    - farmer must be APPROVED
    - listing must be ACTIVE
    - listing must have quantity > 0
    """
    query = (
        select(Produce)
        .where(Produce.status == ProduceStatus.ACTIVE.value)
        .where(Produce.quantity > 0)
        .order_by(Produce.created_at.desc())
    )

    if crop:
        query = query.where(Produce.crop.ilike(f"%{crop}%"))
    if location:
        query = query.where(Produce.location.ilike(f"%{location}%"))
    if max_price is not None:
        query = query.where(Produce.price_per_unit <= max_price)

    produces = db.scalars(query).all()

    results: list[MarketplaceProduceResponse] = []
    for produce in produces:
        if _is_marketplace_eligible(db, produce):
            results.append(MarketplaceProduceResponse.from_produce(produce))

    return results


@router.get(
    "/produce/{produce_id}",
    response_model=MarketplaceProduceResponse,
    summary="Get marketplace-eligible produce detail",
)
def get_marketplace_produce(
    produce_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> MarketplaceProduceResponse:
    """Return a produce detail only if it is marketplace-eligible.

    Ineligible or nonexistent listings return 404.
    """
    produce = db.get(Produce, produce_id)
    if produce is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce with id={produce_id} not found",
        )

    if not _is_marketplace_eligible(db, produce):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce with id={produce_id} not found",
        )

    return MarketplaceProduceResponse.from_produce(produce)
