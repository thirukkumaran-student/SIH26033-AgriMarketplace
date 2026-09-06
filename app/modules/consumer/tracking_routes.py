"""Consumer Shipment Tracking Routes.

- GET    /api/consumer/shipments           -> list shipments for the authenticated consumer
- GET    /api/consumer/shipments/{id}  -> get one shipment

CONSUMER sees ONLY shipments belonging to their own orders.
Ownership enforced through DB: Shipment -> Order -> buyer_id.

This module consumes the existing Shipment + Order system.
P5 owns the logistics engine; this module only reads data.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.shipment import ShipmentResponse, ShipmentDetailResponse

router = APIRouter(prefix="/api/consumer", tags=["consumer"])
DbSession = Annotated[Session, Depends(get_db)]


def _get_shipment_for_consumer(db: Session, shipment_id: int, consumer_id: int) -> Shipment:
    """Return a shipment if it belongs to the consumer's orders.

    Ownership chain: Shipment -> Order -> buyer_id == consumer_id
    Returns 404 for nonexistent or unauthorized shipments.
    """
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id={shipment_id} not found",
        )

    # Verify ownership: the shipment's order must belong to this consumer
    order = db.scalar(select(Order).where(Order.id == shipment.order_id))
    if order is None or order.buyer_id != consumer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id={shipment_id} not found",
        )

    return shipment


def _build_shipment_response(shipment: Shipment, order: Order) -> ShipmentResponse:
    """Build a ShipmentResponse from a Shipment and its Order."""
    return ShipmentResponse(
        id=shipment.id,
        order_id=shipment.order_id,
        produce_name=order.produce.crop if order.produce else "Unknown",
        crop=order.produce.crop if order.produce else "Unknown",
        order_status=order.status,
        status=shipment.status,
        pickup_location=shipment.pickup_location,
        destination=shipment.destination,
        estimated_delivery=shipment.estimated_delivery,
        logistics_cost=shipment.logistics_cost,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )


@router.get(
    "/shipments",
    response_model=list[ShipmentResponse],
    summary="List shipments for the consumer",
)
def list_consumer_shipments(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> list[ShipmentResponse]:
    """Return all shipments belonging to the authenticated consumer's orders.

    Only shipments linked to orders where the consumer is the buyer are returned.
    """
    # Get all orders for this consumer
    consumer_orders = db.scalars(
        select(Order).where(Order.buyer_id == current_user.id)
    ).all()

    if not consumer_orders:
        return []

    # Get all shipments for those orders
    order_ids = [o.id for o in consumer_orders]
    consumer_shipments = db.scalars(
        select(Shipment).where(Shipment.order_id.in_(order_ids))
    ).all()

    if not consumer_shipments:
        return []

    # Build responses with order context
    responses = []
    for shipment in consumer_shipments:
        order = db.scalar(select(Order).where(Order.id == shipment.order_id))
        if order:
            responses.append(_build_shipment_response(shipment, order))

    return responses


@router.get(
    "/shipments/{shipment_id}",
    response_model=ShipmentDetailResponse,
    summary="Get a shipment by ID",
)
def get_consumer_shipment(
    shipment_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.CONSUMER))],
) -> ShipmentDetailResponse:
    """Return a single shipment if it belongs to the authenticated consumer's orders.

    Unauthorized or non-owned shipments return 404.
    """
    shipment = _get_shipment_for_consumer(db, shipment_id, current_user.id)

    order = db.scalar(select(Order).where(Order.id == shipment.order_id))
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Order not found for shipment",
        )

    return ShipmentDetailResponse(
        id=shipment.id,
        order_id=shipment.order_id,
        produce_name=order.produce.crop if order.produce else "Unknown",
        crop=order.produce.crop if order.produce else "Unknown",
        order_status=order.status,
        status=shipment.status,
        pickup_location=shipment.pickup_location,
        destination=shipment.destination,
        estimated_delivery=shipment.estimated_delivery,
        logistics_cost=shipment.logistics_cost,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )
