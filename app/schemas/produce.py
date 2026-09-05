"""Pydantic schemas for Produce payloads and responses.

The ``farmer_id`` is taken from the authenticated JWT — it is never
accepted as user input.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProduceStatus


class ProduceCreate(BaseModel):
    """Payload for POST /api/produce."""

    crop: str = Field(min_length=1, max_length=200, description="Crop name (e.g. Wheat, Rice)")
    category: str = Field(min_length=1, max_length=100, description="Category (e.g. Cereals, Vegetables)")
    quantity: int = Field(gt=0, description="Quantity available (> 0)")
    unit: str = Field(min_length=1, max_length=30, description="Unit (kg, quintal, ton, piece)")
    price_per_unit: float = Field(ge=0, description="Price per unit (>= 0)")
    location: str = Field(min_length=1, max_length=500, description="Farm/location address")
    harvest_date: date | None = Field(default=None, description="Harvest date")
    quality_grade: str | None = Field(default=None, max_length=20, description="Quality grade (A, B, C, Premium)")
    image: str | None = Field(default=None, max_length=500, description="Image URL")


class ProduceUpdate(BaseModel):
    """Payload for PATCH /api/produce/{id}.  All fields optional."""

    crop: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: int | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    price_per_unit: float | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, min_length=1, max_length=500)
    harvest_date: date | None = None
    quality_grade: str | None = Field(default=None, max_length=20)
    image: str | None = Field(default=None, max_length=500)
    status: ProduceStatus | None = None


class ProduceResponse(BaseModel):
    """Representation of a produce listing returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    crop: str
    category: str
    quantity: int
    unit: str
    price_per_unit: float
    location: str
    harvest_date: date | None
    quality_grade: str | None
    image: str | None
    status: ProduceStatus
    created_at: datetime
    updated_at: datetime
