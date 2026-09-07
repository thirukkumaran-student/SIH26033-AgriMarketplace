"""Farmer Produce Routes.

- POST   /api/produce              -> create listing (FARMER, verified only)
- GET    /api/produce              -> list produce (any authenticated user)
- GET    /api/produce/{id}         -> retrieve single listing
- PATCH  /api/produce/{id}         -> update own listing
- DELETE /api/produce/{id}         -> delete own listing

CRUD operations (create / update / delete) require:
  1. Valid JWT with role = FARMER
  2. Farmer must have APPROVED verification

Reading (GET) requires only a valid JWT.
"""
from decimal import Decimal
from datetime import date, datetime, timezone
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
from app.schemas.produce import ProduceCreate, ProduceResponse, ProduceUpdate


def _get_verification_status(db: Session, farmer_id: int) -> str:
    """Return the farmer's overall verification status string.

    Mirrors the logic used by /api/verification/status so produce status
    updates can reuse the same APPROVED gate.
    """
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

router = APIRouter(prefix="/api/produce", tags=["produce"])
DbSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _verify_farmer_approved(db: Session, farmer_id: int) -> None:
    """Raise 403 if the farmer's documents are not all APPROVED."""
    docs = db.scalars(
        select(VerificationDocument).where(VerificationDocument.user_id == farmer_id)
    ).all()

    if not docs:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You have not submitted any verification documents. "
                "Please submit documents via POST /api/verification/documents first."
            ),
        )

    statuses = {d.status for d in docs}
    if VerificationStatus.PENDING.value in statuses:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your farmer verification is still PENDING. "
                "You must be APPROVED before creating produce listings."
            ),
        )
    if VerificationStatus.REJECTED.value in statuses:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your farmer verification has been REJECTED. "
                "You must be APPROVED before creating produce listings."
            ),
        )


def _get_produce_or_404(db: Session, produce_id: int) -> Produce:
    """Return the produce item or raise 404."""
    produce = db.get(Produce, produce_id)
    if produce is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce with id={produce_id} not found",
        )
    return produce


# ---------------------------------------------------------------------------
# POST /api/produce  —  create listing
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=ProduceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a produce listing",
)
def create_produce(
    payload: ProduceCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> Produce:
    """Create a produce listing. Only verified APPROVED farmers allowed."""
    _verify_farmer_approved(db, current_user.id)

    produce = Produce(
        farmer_id=current_user.id,
        crop=payload.crop,
        category=payload.category,
        quantity=payload.quantity,
        unit=payload.unit,
        price_per_unit=payload.price_per_unit,
        location=payload.location,
        harvest_date=payload.harvest_date,
        quality_grade=payload.quality_grade,
        image=payload.image,
        status=ProduceStatus.ACTIVE.value,
    )
    db.add(produce)
    db.commit()
    db.refresh(produce)
    return produce


# ---------------------------------------------------------------------------
# GET /api/produce  —  list produce
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=list[ProduceResponse],
    summary="List produce listings",
)
def list_produce(
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
    crop: str | None = Query(default=None, description="Filter by crop name"),
    category: str | None = Query(default=None, description="Filter by category"),
    status_filter: ProduceStatus | None = Query(default=None, alias="status", description="Filter by status"),
    location: str | None = Query(default=None, description="Filter by location (contains)"),
    min_price: Decimal | None = Query(default=None, ge=0, description="Min price per unit"),
    max_price: Decimal | None = Query(default=None, ge=0, description="Max price per unit"),
    farmer_id: int | None = Query(default=None, description="Filter by farmer user id"),
) -> list[Produce]:
    """Return produce listings with optional filters.

    This endpoint is the SINGLE SOURCE OF TRUTH for produce data.
    Future Marketplace / Consumer modules will consume this API.
    """
    query = select(Produce)

    if crop:
        query = query.where(Produce.crop.ilike(f"%{crop}%"))
    if category:
        query = query.where(Produce.category.ilike(f"%{category}%"))
    if status_filter:
        query = query.where(Produce.status == status_filter.value)
    if location:
        query = query.where(Produce.location.ilike(f"%{location}%"))
    if min_price is not None:
        query = query.where(Produce.price_per_unit >= min_price)
    if max_price is not None:
        query = query.where(Produce.price_per_unit <= max_price)
    if farmer_id is not None:
        query = query.where(Produce.farmer_id == farmer_id)

    query = query.order_by(Produce.created_at.desc())
    return list(db.scalars(query).all())


# ---------------------------------------------------------------------------
# GET /api/produce/{id}  —  retrieve single listing
# ---------------------------------------------------------------------------


@router.get(
    "/{produce_id}",
    response_model=ProduceResponse,
    summary="Get a produce listing",
)
def get_produce(
    produce_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Produce:
    """Return a single produce listing by id."""
    return _get_produce_or_404(db, produce_id)


# ---------------------------------------------------------------------------
# PATCH /api/produce/{id}  —  update own listing
# ---------------------------------------------------------------------------


@router.patch(
    "/{produce_id}",
    response_model=ProduceResponse,
    summary="Update a produce listing",
)
def update_produce(
    produce_id: int,
    payload: ProduceUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> Produce:
    """Update a produce listing. Only the owning farmer may update.

    Status changes require the farmer to be APPROVED, and a listing may not
    be marked SOLD_OUT while available quantity is still greater than 0.
    """
    produce = _get_produce_or_404(db, produce_id)

    if produce.farmer_id != current_user.id:
        # Return 404 to avoid leaking the existence of another farmer's resource
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce with id={produce_id} not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields to update",
        )

    if "status" in update_data:
        # Status changes require APPROVED verification (reuses the same gate
        # as produce creation).
        verification_status = _get_verification_status(db, current_user.id)
        if verification_status != VerificationStatus.APPROVED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You must be APPROVED before you can change listing status. "
                    f"Current verification status: {verification_status}."
                ),
            )

        new_status = update_data["status"]
        if hasattr(new_status, "value"):
            new_status = new_status.value
        update_data["status"] = new_status

        # A listing may not be marked SOLD_OUT while stock is still available.
        if new_status == ProduceStatus.SOLD_OUT.value and produce.quantity > 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Cannot mark listing as SOLD_OUT while quantity is still greater than 0. "
                    "Reduce quantity to 0 first, or set status to INACTIVE."
                ),
            )

    for field, value in update_data.items():
        setattr(produce, field, value)

    db.commit()
    db.refresh(produce)
    return produce


# ---------------------------------------------------------------------------
# DELETE /api/produce/{id}  —  delete own listing
# ---------------------------------------------------------------------------


@router.delete(
    "/{produce_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a produce listing",
)
def delete_produce(
    produce_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> None:
    """Delete a produce listing. Only the owning farmer may delete."""
    produce = _get_produce_or_404(db, produce_id)

    if produce.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce with id={produce_id} not found",
        )

    db.delete(produce)
    db.commit()
