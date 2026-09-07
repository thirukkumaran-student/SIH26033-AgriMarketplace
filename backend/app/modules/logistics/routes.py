from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from .models import Shipment
from .service import logistics_service


router = APIRouter(
    prefix="/api/logistics",
    tags=["Logistics"],
)


class ShipmentCreateRequest(BaseModel):
    order_id: int
    pickup_location: str
    delivery_location: str
    logistics_cost: float = 0.0
    distance: float = 0.0


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    logistics_partner_id: int | None
    pickup_location: str
    delivery_location: str
    logistics_cost: float
    distance: float
    route_sequence: str | None
    status: str

    class Config:
        from_attributes = True


class RouteOptimizeRequest(BaseModel):
    distance_matrix: list[list[int]]
    start_index: int = 0


class RouteOptimizeResponse(BaseModel):
    route: list[int]
    total_distance: int


def update_shipment_status(
    shipment_id: int,
    next_status: str,
    db: Session,
):
    shipment = db.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found.",
        )

    try:
        logistics_service.transition_shipment(
            shipment,
            next_status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    db.commit()
    db.refresh(shipment)

    return shipment


@router.post(
    "/routes/optimize",
    response_model=RouteOptimizeResponse,
)
def optimize_route(request: RouteOptimizeRequest):
    try:
        return logistics_service.optimize_route(
            distance_matrix=request.distance_matrix,
            start_index=request.start_index,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/shipments",
    response_model=ShipmentResponse,
)
def create_shipment(
    request: ShipmentCreateRequest,
    db: Session = Depends(get_db),
):
    shipment = Shipment(
        order_id=request.order_id,
        pickup_location=request.pickup_location,
        delivery_location=request.delivery_location,
        logistics_cost=request.logistics_cost,
        distance=request.distance,
        status="CREATED",
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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
):
    shipment = db.get(Shipment, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found.",
        )

    return shipment


@router.get(
    "/shipments",
    response_model=list[ShipmentResponse],
)
def get_shipments(
    db: Session = Depends(get_db),
):
    return db.query(Shipment).all()