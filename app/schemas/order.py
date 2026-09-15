"""Pydantic schemas for Order payloads and responses.

Key design: the buyer submits ``produce_id`` and ``quantity``.
For platform-financed bulk orders, ``relationship_id`` identifies the
buyer's already-established active financing relationship.
``farmer_id``, ``unit_price``, and ``total_amount`` are determined by the
backend from the Produce listing and the owning farmer.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from app.core.enums import OrderStatus, PaymentMethod, PaymentStatus


class OrderCreate(BaseModel):
    """Payload for POST /api/orders.

    buyer provides:
    - produce_id
    - quantity
    - relationship_id only when using platform financing
    """

    produce_id: int = Field(gt=0, description="Produce listing id to order from")
    quantity: int = Field(gt=0, description="Quantity to order (> 0)")
    relationship_id: int | None = Field(
        default=None,
        gt=0,
        description="Active financing relationship for platform-financed orders",
    )


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


class OrderPaymentRequest(BaseModel):
    """Only the mock method comes from the buyer; amount stays authoritative."""

    model_config = ConfigDict(extra="forbid")

    payment_method: PaymentMethod


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
    unit_price: Decimal
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod | None
    payment_reference: str | None
    paid_at: datetime | None
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
    unit_price: Decimal
    total_amount: Decimal
    unit: str
    available_stock: int
    status: str
