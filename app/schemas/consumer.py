"""Pydantic schemas for Consumer Profile payloads and responses.

The user_id is taken from the authenticated JWT — it is never accepted as user
input.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import ProduceStatus


class ConsumerProfileCreate(BaseModel):
    """Payload for POST /api/consumer/profile (create own profile)."""

    phone: str | None = Field(default=None, max_length=20, description="Contact number")
    address: str | None = Field(default=None, max_length=500, description="Street address")
    city: str | None = Field(default=None, max_length=100, description="City")
    state: str | None = Field(default=None, max_length=100, description="State")
    pincode: str | None = Field(default=None, max_length=20, description="PIN code")

    @field_validator("phone")
    @classmethod
    def phone_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Phone must not be blank if supplied")
        return value

    @field_validator("address")
    @classmethod
    def address_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Address must not be blank if supplied")
        return value

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("City must not be blank if supplied")
        return value

    @field_validator("state")
    @classmethod
    def state_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("State must not be blank if supplied")
        return value

    @field_validator("pincode")
    @classmethod
    def pincode_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Pincode must not be blank if supplied")
        if value is not None and len(value.strip()) < 3:
            raise ValueError("Pincode looks too short")
        return value


class ConsumerProfileUpdate(BaseModel):
    """Payload for PUT /api/consumer/profile (update own profile).

    All fields optional — only provided fields are overwritten.
    """

    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=20)

    @field_validator("phone")
    @classmethod
    def phone_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Phone must not be blank if supplied")
        return value

    @field_validator("address")
    @classmethod
    def address_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Address must not be blank if supplied")
        return value

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("City must not be blank if supplied")
        return value

    @field_validator("state")
    @classmethod
    def state_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("State must not be blank if supplied")
        return value

    @field_validator("pincode")
    @classmethod
    def pincode_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Pincode must not be blank if supplied")
        if value is not None and len(value.strip()) < 3:
            raise ValueError("Pincode looks too short")
        return value


class ConsumerProfileResponse(BaseModel):
    """Public representation of a consumer profile."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    phone: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    created_at: datetime
    updated_at: datetime


class MarketplaceProduceResponse(BaseModel):
    """Consumer-facing representation of a marketplace-eligible produce listing.

    Built ONLY from fields that exist on the Produce model. This schema is used
    by the Marketplace endpoints and does NOT create any new database table.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
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

    @classmethod
    def from_produce(cls, produce: "Produce") -> "MarketplaceProduceResponse":
        """Build a marketplace response from a Produce ORM instance."""
        from app.models.produce import Produce

        return cls(
            id=produce.id,
            crop=produce.crop,
            category=produce.category,
            quantity=produce.quantity,
            unit=produce.unit,
            price_per_unit=produce.price_per_unit,
            location=produce.location,
            harvest_date=produce.harvest_date,
            quality_grade=produce.quality_grade,
            image=produce.image,
            status=ProduceStatus(produce.status),
        )
