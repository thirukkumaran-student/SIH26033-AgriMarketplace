"""Admin Dispute Management Routes.

- GET    /api/admin/disputes            -> list all disputes
- GET    /api/admin/disputes/{id}  -> get a dispute detail
- POST   /api/admin/disputes/{id}/resolve -> resolve a dispute

Only ADMIN can access these endpoints.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.dispute import Dispute
from app.models.order import Order
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.dispute import DisputeDetailResponse, DisputeListResponse, DisputeResolution

router = APIRouter(prefix="/api/admin", tags=["admin"])
DbSession = Annotated[Session, Depends(get_db)]


def _get_dispute_or_404(db: Session, dispute_id: int) -> Dispute:
    """Return a dispute or raise 404."""
    dispute = db.get(Dispute, dispute_id)
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispute with id={dispute_id} not found",
        )
    return dispute


@router.get(
    "/disputes",
    response_model=list[DisputeListResponse],
    summary="List all disputes",
)
def list_disputes(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> list[DisputeListResponse]:
    """Return all disputes with basic order information.

    Supports optional status filtering.
    """
    query = select(Dispute).order_by(Dispute.created_at.desc())
    disputes = db.scalars(query).all()

    results = []
    for dispute in disputes:
        order = db.scalar(select(Order).where(Order.id == dispute.order_id))
        results.append(
            DisputeListResponse(
                id=dispute.id,
                order_id=dispute.order_id,
                raised_by=dispute.raised_by,
                reason=dispute.reason,
                status=dispute.status,
                resolution=dispute.resolution,
                created_at=dispute.created_at,
                updated_at=dispute.updated_at,
                crop=order.produce.crop if order and order.produce else "Unknown",
                order_status=order.status if order else "Unknown",
            )
        )

    return results


@router.get(
    "/disputes/{dispute_id}",
    response_model=DisputeDetailResponse,
    summary="Get dispute details",
)
def get_dispute(
    dispute_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> DisputeDetailResponse:
    """Return detailed dispute information including order and produce data."""
    dispute = _get_dispute_or_404(db, dispute_id)

    order = db.scalar(select(Order).where(Order.id == dispute.order_id))

    return DisputeDetailResponse(
        id=dispute.id,
        order_id=dispute.order_id,
        raised_by=dispute.raised_by,
        reason=dispute.reason,
        description=dispute.description,
        status=dispute.status,
        resolution=dispute.resolution,
        admin_remarks=dispute.admin_remarks,
        resolved_by=dispute.resolved_by,
        created_at=dispute.created_at,
        updated_at=dispute.updated_at,
        resolved_at=dispute.resolved_at,
        crop=order.produce.crop if order and order.produce else "Unknown",
        order_status=order.status if order else "Unknown",
        order_quantity=order.quantity,
        order_total_amount=order.total_amount,
    )


@router.post(
    "/disputes/{dispute_id}/resolve",
    response_model=DisputeDetailResponse,
    summary="Resolve a dispute",
)
def resolve_dispute(
    dispute_id: int,
    payload: DisputeResolution,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> Dispute:
    """Resolve a dispute with ACCEPTED, REJECTED, or PARTIAL.

    Only ADMIN can resolve disputes.
    Already resolved disputes cannot be resolved again.
    The resolved_by field is set from the authenticated admin's JWT.
    """
    dispute = _get_dispute_or_404(db, dispute_id)

    # Check already resolved
    if dispute.status != "OPEN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dispute is already resolved with status {dispute.status}",
        )

    # Validate resolution value
    valid_resolutions = {"ACCEPTED", "REJECTED", "PARTIAL"}
    if payload.resolution not in valid_resolutions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid resolution: {payload.resolution}. "
                f"Allowed values: {', '.join(sorted(valid_resolutions))}"
            ),
        )

    # Perform resolution
    dispute.status = payload.resolution
    dispute.resolution = payload.resolution
    dispute.admin_remarks = payload.admin_remarks
    dispute.resolved_by = current_user.id
    dispute.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(dispute)
    return dispute
