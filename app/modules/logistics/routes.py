from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.handoff import Handoff
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.user import User
from app.modules.auth.dependencies import require_role

from .service import logistics_service


router = APIRouter(
    prefix="/api/logistics",
    tags=["Logistics"],
)

DbSession = Annotated[Session, Depends(get_db)]
LogisticsUser = Annotated[
    User,
    Depends(require_role(Role.LOGISTICS)),
]


class ShipmentCreateRequest(BaseModel):
    order_id: int
    pickup_location: str
    destination: str
    logistics_cost: Decimal = Decimal("0.00")
    estimated_delivery: datetime | None = None


class ShipmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    status: str
    pickup_location: str
    destination: str
    estimated_delivery: datetime | None
    logistics_cost: Decimal
    created_at: datetime
    updated_at: datetime


class RouteOptimizeRequest(BaseModel):
    distance_matrix: list[list[int]]
    start_index: int = 0


class RouteOptimizeResponse(BaseModel):
    route: list[int]
    total_distance: int


class HandoffCreateRequest(BaseModel):
    from_party: str
    to_party: str
    location: str
    remarks: str | None = None


class HandoffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipment_id: int
    from_party: str
    to_party: str
    location: str
    remarks: str | None
    timestamp: datetime


def update_shipment_status(
    shipment_id: int,
    next_status: str,
    db: Session,
):
    shipment = db.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    try:
        logistics_service.transition_shipment(
            shipment,
            next_status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    db.commit()
    db.refresh(shipment)

    return shipment


@router.post(
    "/routes/optimize",
    response_model=RouteOptimizeResponse,
)
def optimize_route(
    request: RouteOptimizeRequest,
    current_user: LogisticsUser,
):
    try:
        return logistics_service.optimize_route(
            distance_matrix=request.distance_matrix,
            start_index=request.start_index,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/shipments",
    response_model=ShipmentResponse,
)
def create_shipment(
    request: ShipmentCreateRequest,
    db: DbSession,
    current_user: LogisticsUser,
):
    order = db.get(Order, request.order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    shipment = Shipment(
        order_id=request.order_id,
        pickup_location=request.pickup_location,
        destination=request.destination,
        estimated_delivery=request.estimated_delivery,
        logistics_cost=request.logistics_cost,
        status="PENDING",
    )

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return shipment


@router.post(
    "/shipments/{shipment_id}/assign",
    response_model=ShipmentResponse,
)
def assign_shipment(
    shipment_id: int,
    db: DbSession,
    current_user: LogisticsUser,
):
    return update_shipment_status(
        shipment_id,
        "ASSIGNED",
        db,
    )


@router.post(
    "/shipments/{shipment_id}/pickup",
    response_model=ShipmentResponse,
)
def pickup_shipment(
    shipment_id: int,
    db: DbSession,
    current_user: LogisticsUser,
):
    return update_shipment_status(
        shipment_id,
        "PICKED_UP",
        db,
    )


@router.post(
    "/shipments/{shipment_id}/transit",
    response_model=ShipmentResponse,
)
def start_transit(
    shipment_id: int,
    db: DbSession,
    current_user: LogisticsUser,
):
    return update_shipment_status(
        shipment_id,
        "IN_TRANSIT",
        db,
    )


@router.post(
    "/shipments/{shipment_id}/deliver",
    response_model=ShipmentResponse,
)
def deliver_shipment(
    shipment_id: int,
    db: DbSession,
    current_user: LogisticsUser,
):
    return update_shipment_status(
        shipment_id,
        "DELIVERED",
        db,
    )


@router.get(
    "/shipments/{shipment_id}",
    response_model=ShipmentResponse,
)
def get_shipment(
    shipment_id: int,
    db: DbSession,
    current_user: LogisticsUser,
):
    shipment = db.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    return shipment


@router.get(
    "/shipments",
    response_model=list[ShipmentResponse],
)
def get_shipments(
    db: DbSession,
    current_user: LogisticsUser,
):
    return db.query(Shipment).all()


@router.post(
    "/handoff/{shipment_id}",
    response_model=HandoffResponse,
)
def create_handoff(
    shipment_id: int,
    request: HandoffCreateRequest,
    db: DbSession,
    current_user: LogisticsUser,
):
    shipment = db.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    handoff = Handoff(
        shipment_id=shipment_id,
        from_party=request.from_party,
        to_party=request.to_party,
        location=request.location,
        remarks=request.remarks,
    )

    db.add(handoff)
    db.commit()
    db.refresh(handoff)

    return handoff


@router.get(
    "/handoff/{shipment_id}",
    response_model=list[HandoffResponse],
)
def get_handoffs(
    shipment_id: int,
    db: DbSession,
    current_user: LogisticsUser,
):
    shipment = db.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    return (
        db.query(Handoff)
        .filter(Handoff.shipment_id == shipment_id)
        .order_by(Handoff.timestamp)
        .all()
    )