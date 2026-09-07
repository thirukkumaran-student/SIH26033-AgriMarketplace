"""Pydantic schemas for Shipment payloads and responses.

Minimal schemas for the farmer shipment view. Logistics (P5) will extend
this later.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ShipmentStatus


class ShipmentResponse(BaseModel):
    """Public representation of a shipment returned to the farmer."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    produce_name: str  # populated from Order -> Produce for convenience
    crop: str  # populated from Order -> Produce
    order_status: str  # the order's status, for context
    status: ShipmentStatus
    pickup_location: str
    destination: str
    estimated_delivery: datetime | None
    logistics_cost: float
    created_at: datetime
    updated_at: datetime


class ShipmentDetailResponse(BaseModel):
    """Detailed shipment view for GET /api/farmer/shipments/{shipment_id}."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    produce_name: str
    crop: str
    order_status: str
    status: ShipmentStatus
    pickup_location: str
    destination: str
    estimated_delivery: datetime | None
    logistics_cost: float
    created_at: datetime
    updated_at: datetime
