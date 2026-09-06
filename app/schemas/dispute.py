"""Pydantic schemas for Dispute payloads and responses.

Consumer creates disputes with reason and description.
Admin resolves disputes with resolution and remarks.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DisputeCreate(BaseModel):
    """Payload for POST /api/consumer/disputes.

    Consumer provides:
    - order_id (the order to dispute)
    - reason (short reason)
    - description (optional detailed description)
    """

    order_id: int = Field(gt=0, description="Order ID to dispute")
    reason: str = Field(min_length=1, max_length=200, description="Reason for the dispute")
    description: str | None = Field(default=None, max_length=2000, description="Optional detailed description")


class DisputeResponse(BaseModel):
    """Public representation of a dispute returned to the consumer."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    raised_by: int
    reason: str
    description: str | None
    status: str
    resolution: str | None
    created_at: datetime
    updated_at: datetime


class DisputeDetailResponse(BaseModel):
    """Detailed dispute view for admin."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    raised_by: int
    reason: str
    description: str | None
    status: str
    resolution: str | None
    admin_remarks: str | None
    resolved_by: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    crop: str = "Unknown"
    order_status: str = "Unknown"
    order_quantity: int = 0
    order_total_amount: float = 0.0


class DisputeResolution(BaseModel):
    """Payload for admin dispute resolution."""

    resolution: str = Field(
        description="Resolution: ACCEPTED, REJECTED, or PARTIAL",
        max_length=20,
    )
    admin_remarks: str | None = Field(
        default=None,
        max_length=2000,
        description="Admin remarks for the resolution",
    )


class DisputeListResponse(BaseModel):
    """List view of disputes for admin."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    raised_by: int
    reason: str
    status: str
    resolution: str | None
    created_at: datetime
    updated_at: datetime
    crop: str = "Unknown"
    order_status: str = "Unknown"