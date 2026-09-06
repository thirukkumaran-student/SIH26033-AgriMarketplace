"""Orders Routes.

- POST   /api/orders                     -> create an order (CONSUMER / BULK_BUYER)
- GET    /api/orders                     -> list orders relevant to the user
- GET    /api/orders/{order_id}          -> get a single order
- PATCH  /api/orders/{order_id}/status   -> update order status

Status transitions allowed:
    PENDING  -> CONFIRMED   (by farmer)
    PENDING  -> CANCELLED   (by buyer)
    CONFIRMED -> COMPLETED  (by farmer)

These transitions are enforced; others return 422.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import OrderStatus, ProduceStatus, Role, VerificationStatus
from app.models.farmer import VerificationDocument
from app.models.order import Order
from app.models.produce import Produce
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.order import OrderCreate, OrderReviewRequest, OrderReviewResponse, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])
DbSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


VALID_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.PENDING.value: {OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value},
    OrderStatus.CONFIRMED.value: {OrderStatus.COMPLETED.value},
}


def _get_farmer_verification_status(db: Session, farmer_id: int) -> str:
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


def _order_should_show_to_user(order: Order, user: User) -> bool:
    """Return True if *user* is allowed to see this order."""
    if user.role == Role.ADMIN.value:
        return True
    if user.role == Role.FARMER.value and order.farmer_id == user.id:
        return True
    if user.role in {Role.CONSUMER.value, Role.BULK_BUYER.value} and order.buyer_id == user.id:
        return True
    return False


def _get_order_or_404(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id={order_id} not found")
    return order


def _get_order_or_404_for_user(db: Session, order_id: int, user: User) -> Order:
    order = _get_order_or_404(db, order_id)
    if not _order_should_show_to_user(order, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this order")
    return order


def _get_valid_transition(from_status: str, to_status: str) -> str:
    if to_status not in VALID_TRANSITIONS.get(from_status, set()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition: {from_status} -> {to_status}. "
                f"Allowed transitions from {from_status}: "
                f"{', '.join(sorted(VALID_TRANSITIONS.get(from_status, set())))}"
            ),
        )
    return to_status


# ---------------------------------------------------------------------------
# POST /api/orders  —  create order
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order",
)
def create_order(
    payload: OrderCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER, Role.BULK_BUYER))],
) -> Order:
    """Create an order for a produce listing.

    Only CONSUMER or BULK_BUYER may create orders.
    - produce_id must exist and be ACTIVE with enough stock
    - farmer_id and unit_price come from the Produce listing
    - total_amount = quantity * unit_price
    - farmer cannot order their own produce
    - produce quantity is reduced on success
    """

    # 1. Find the produce listing
    produce = db.scalar(select(Produce).where(Produce.id == payload.produce_id))
    if produce is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce listing with id={payload.produce_id} not found",
        )

    # 2. Check produce is available
    if produce.status != ProduceStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produce listing is not available for ordering",
        )

    # 3. Validate quantity
    quantity = payload.quantity
    if produce.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {produce.quantity} {produce.unit} available, requested {quantity}",
        )

    # 4. Prevent farmer from ordering their own produce
    if produce.farmer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot order your own produce",
        )

    # 5. Check farmer is APPROVED (marketplace eligibility)
    if _get_farmer_verification_status(db, produce.farmer_id) != VerificationStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produce listing is not available for ordering",
        )

    # 6. Get farmer_id and unit_price from the producing farmer
    farmer_id = produce.farmer_id
    unit_price = produce.price_per_unit
    total_amount = quantity * unit_price

    # 7. Create the order
    order = Order(
        produce_id=payload.produce_id,
        buyer_id=current_user.id,
        farmer_id=farmer_id,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        status=OrderStatus.PENDING.value,
    )

    # 8. Reduce produce stock
    produce.quantity -= quantity

    db.add(order)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create order (stock conflict)",
        )

    db.refresh(order)
    return order


# ---------------------------------------------------------------------------
# POST /api/orders/review  —  order review
# ---------------------------------------------------------------------------


@router.post(
    "/review",
    response_model=OrderReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Review an order before placing it",
)
def review_order(
    payload: OrderReviewRequest,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER, Role.BULK_BUYER))],
) -> dict:
    """Review the current purchase details before finalizing.

    This is a read-only operation:
    - validates produce eligibility and availability
    - validates requested quantity against stock
    - calculates unit_price and total_amount from the DB Produce record
    - does NOT create an order and does NOT decrease stock

    The consumer can then confirm via POST /api/orders.
    """
    # 1. Find the produce listing
    produce = db.scalar(select(Produce).where(Produce.id == payload.produce_id))
    if produce is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produce listing with id={payload.produce_id} not found",
        )

    # 2. Check produce is available
    if produce.status != ProduceStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produce listing is not available for ordering",
        )

    # 3. Validate quantity against available stock
    quantity = payload.quantity
    if produce.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {produce.quantity} {produce.unit} available, requested {quantity}",
        )

    # 4. Prevent farmer from ordering their own produce
    if produce.farmer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot order your own produce",
        )

    # 5. Check farmer is APPROVED (marketplace eligibility)
    if _get_farmer_verification_status(db, produce.farmer_id) != VerificationStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produce listing is not available for ordering",
        )

    # 6. Calculate from DB authoritative values
    unit_price = produce.price_per_unit
    total_amount = quantity * unit_price

    return OrderReviewResponse(
        produce_id=produce.id,
        crop=produce.crop,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        unit=produce.unit,
        available_stock=produce.quantity,
        status=produce.status,
    )


# ---------------------------------------------------------------------------
# GET /api/orders  —  list orders
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=list[OrderResponse],
    summary="List orders",
)
def list_orders(
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Order]:
    """Return orders relevant to the authenticated user.

    FARMER: orders for their produce
    CONSUMER/BULK_BUYER: their own orders
    ADMIN: all orders
    """
    if current_user.role == Role.ADMIN.value:
        query = select(Order).order_by(Order.created_at.desc())
        return list(db.scalars(query).all())

    if current_user.role == Role.FARMER.value:
        query = select(Order).where(Order.farmer_id == current_user.id).order_by(Order.created_at.desc())
        return list(db.scalars(query).all())

    # CONSUMER or BULK_BUYER
    query = select(Order).where(Order.buyer_id == current_user.id).order_by(Order.created_at.desc())
    return list(db.scalars(query).all())


# ---------------------------------------------------------------------------
# GET /api/orders/{order_id}  —  get single order
# ---------------------------------------------------------------------------


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get an order",
)
def get_order(
    order_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Order:
    """Return a single order if the user is authorized to see it."""
    return _get_order_or_404_for_user(db, order_id, current_user)


# ---------------------------------------------------------------------------
# PATCH /api/orders/{order_id}/status  —  update status
# ---------------------------------------------------------------------------


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Order:
    """Update the status of an order.

    Valid transitions:
        - Buyer: PENDING -> CANCELLED (restores stock)
        - Farmer: PENDING -> CONFIRMED
        - Farmer: CONFIRMED -> COMPLETED
        - Admin: any allowed transition
    """

    order = _get_order_or_404_for_user(db, order_id, current_user)

    # Validate the transition
    new_status = _get_valid_transition(order.status, payload.status.value)
    to_status = payload.status.value

    # Check role permissions
    user_role = current_user.role

    if user_role == Role.ADMIN.value:
        # Admin can transition any valid way
        pass
    elif user_role == Role.FARMER.value:
        if order.farmer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update orders for your own produce",
            )
        # Farmer: PENDING -> CONFIRMED, CONFIRMED -> COMPLETED
        if order.status == OrderStatus.PENDING.value and to_status != OrderStatus.CONFIRMED.value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Farmer can only confirm PENDING orders")
        if order.status == OrderStatus.CONFIRMED.value and to_status != OrderStatus.COMPLETED.value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Farmer can only complete CONFIRMED orders")
    elif user_role in {Role.CONSUMER.value, Role.BULK_BUYER.value}:
        if order.buyer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own orders",
            )
        # Buyer: PENDING -> CANCELLED only
        if order.status != OrderStatus.PENDING.value or to_status != OrderStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="You can only cancel your own PENDING orders",
            )

    # Perform the transition
    order.status = to_status

    # If CANCELLED, restore stock
    if to_status == OrderStatus.CANCELLED.value:
        produce = db.get(Produce, order.produce_id)
        if produce:
            produce.quantity += order.quantity

    db.commit()
    db.refresh(order)
    return order