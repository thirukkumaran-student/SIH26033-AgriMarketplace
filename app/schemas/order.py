"""Pydantic schemas for Order payloads and responses.

Key design: the buyer may only submit ``produce_id`` and ``quantity``.
``farmer_id``, ``unit_price``, and ``total_amount`` are determined by the
backend from the Produce listing and the owning farmer.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import OrderStatus


class OrderCreate(BaseModel):
    """Payload for POST /api/orders.

    buyer provides only:
    - produce_id (which listing to buy from)
    - quantity (how many units)
    """

    produce_id: int = Field(gt=0, description="Produce listing id to order from")
    quantity: int = Field(gt=0, description="Quantity to order (> 0)")


class OrderReviewRequest(BaseModel):
    """Payload for POST /api/orders/review.

    Consumer provides only:
    - produce_id (which listing to review)
    - quantity (how many units to review)
    """

    produce_id: int = Field(gt=0, description="Produce listing id to review")
    quantity: int = Field(gt=0, description="Quantity to review (> 0)")


class OrderStatusUpdate(BaseModel):
    """Payload for PATCH /api/orders/{order_id}/status.

    Valid status transitions are enforced by the backend; the schema only
    validates that the supplied status is a recognized enum value.
    """

    status: OrderStatus


class OrderResponse(BaseModel):
    """Representation of an order returned by the API.

    The buyer sees their order; the farmer sees theirs (with less detail
    about buyer PII beyond what's needed).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    produce_id: int
    buyer_id: int
    farmer_id: int
    quantity: int
    unit_price: float
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderReviewResponse(BaseModel):
    """Read-only checkout review response.

    Contains the calculated order review information without any
    order creation or stock mutation. The consumer can review this
    before confirming via POST /api/orders.
    """

    model_config = ConfigDict(from_attributes=True)

    produce_id: int
    crop: str
    quantity: int
    unit_price: float
    total_amount: float
    unit: str
    available_stock: int
    status: str
