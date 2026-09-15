"""Farmer Shipment View Routes.

- GET    /api/farmer/shipments                -> list shipments for the authenticated farmer
- GET    /api/farmer/shipments/{shipment_id}  -> get one shipment

SECURITY:
- JWT authentication required
- FARMER role required
- Farmer sees ONLY shipments connected to orders for their own produce
- Ownership enforced in the backend query (Shipment -> Order -> farmer_id)

P5 owns the logistics engine. This module only provides the farmer's view.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role, ShipmentStatus
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.user import User
from app.modules.auth.dependencies import get_current_user, require_role
from app.schemas.shipment import ShipmentDetailResponse, ShipmentResponse

router = APIRouter(prefix="/api/farmer", tags=["farmer"])
DbSession = Annotated[Session, Depends(get_db)]


def _get_shipment_for_farmer(db: Session, shipment_id: int, farmer_id: int) -> Shipment:
    """Return a shipment if it belongs to the farmer's produce orders."""
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id={shipment_id} not found",
        )

    # Verify ownership: the shipment's order must belong to this farmer
    order = db.scalar(select(Order).where(Order.id == shipment.order_id))
    if order is None or order.farmer_id != farmer_id:
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
        logistics_fee_status=shipment.logistics_fee_status,
        logistics_fee_reference=shipment.logistics_fee_reference,
        logistics_fee_collected_at=shipment.logistics_fee_collected_at,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )


@router.get(
    "/shipments",
    response_model=list[ShipmentResponse],
    summary="List shipments for the farmer",
)
def list_farmer_shipments(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> list[ShipmentResponse]:
    """Return all shipments for the authenticated farmer.

    Only shipments linked to orders for this farmer's produce are returned.
    """

    # Get all orders for this farmer
    farmer_orders = db.scalars(
        select(Order).where(Order.farmer_id == current_user.id)
    ).all()

    if not farmer_orders:
        return []

    # Get all shipments for those orders
    order_ids = [o.id for o in farmer_orders]
    farmer_shipments = db.scalars(
        select(Shipment).where(Shipment.order_id.in_(order_ids))
    ).all()

    if not farmer_shipments:
        return []

    # Build enum of allowed statuses for validation
    responses = []
    for shipment in farmer_shipments:
        order = db.scalar(select(Order).where(Order.id == shipment.order_id))
        if order:
            responses.append(_build_shipment_response(shipment, order))

    return responses


@router.get(
    "/shipments/{shipment_id}",
    response_model=ShipmentDetailResponse,
    summary="Get a shipment by ID",
)
def get_farmer_shipment(
    shipment_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.FARMER))],
) -> ShipmentDetailResponse:
    """Return a single shipment if it belongs to the authenticated farmer."""
    shipment = _get_shipment_for_farmer(db, shipment_id, current_user.id)

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
        logistics_fee_status=shipment.logistics_fee_status,
        logistics_fee_reference=shipment.logistics_fee_reference,
        logistics_fee_collected_at=shipment.logistics_fee_collected_at,
        created_at=shipment.created_at,
        updated_at=shipment.updated_at,
    )
