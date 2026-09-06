"""Consumer Dispute Creation Routes.

- POST /api/consumer/disputes  -> raise a dispute against an order

Only CONSUMER can raise disputes.
The consumer can only dispute their own orders.
Only non-CANCELLED orders can be disputed.
Only one open dispute per order is allowed.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import OrderStatus, Role
from app.models.dispute import Dispute
from app.models.order import Order
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.dispute import DisputeCreate, DisputeResponse

router = APIRouter(prefix="/api/consumer", tags=["consumer"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/disputes",
    response_model=DisputeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Raise a dispute against an order",
)
def create_dispute(
    payload: DisputeCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> Dispute:
    """Raise a dispute against an order the consumer owns.

    Rules:
    - Order must exist
    - Order must belong to the authenticated consumer
    - Order must not be CANCELLED
    - Only one OPEN dispute per order is allowed
    """
    # 1. Find the order
    order = db.scalar(select(Order).where(Order.id == payload.order_id))
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={payload.order_id} not found",
        )

    # 2. Verify ownership
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only dispute your own orders",
        )

    # 3. Check order is not CANCELLED
    if order.status == OrderStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled orders cannot be disputed",
        )

    # 4. Check no existing open dispute for this order
    existing = db.scalar(
        select(Dispute)
        .where(Dispute.order_id == payload.order_id)
        .where(Dispute.status == "OPEN")
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An open dispute already exists for order id={payload.order_id}",
        )

    # 5. Create the dispute
    dispute = Dispute(
        order_id=payload.order_id,
        raised_by=current_user.id,
        reason=payload.reason,
        description=payload.description,
        status="OPEN",
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    return dispute
