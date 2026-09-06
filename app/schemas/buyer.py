"""Pydantic schemas for Bulk Buyer Profile."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BuyerProfileCreate(BaseModel):
    """Payload for POST /api/buyer/profile."""

    phone: str | None = Field(
        default=None,
        max_length=20,
        description="Contact number",
    )
    address: str | None = Field(
        default=None,
        max_length=500,
        description="Street address",
    )
    city: str | None = Field(
        default=None,
        max_length=100,
        description="City",
    )
    state: str | None = Field(
        default=None,
        max_length=100,
        description="State",
    )
    pincode: str | None = Field(
        default=None,
        max_length=20,
        description="PIN code",
    )
    financing_preference: str = Field(
        default="NONE",
        description="Whether the buyer wants platform financing",
    )

    @field_validator("phone", "address", "city", "state", "pincode")
    @classmethod
    def fields_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Field must not be blank if supplied")
        return value


class BuyerProfileUpdate(BaseModel):
    """Payload for PUT /api/buyer/profile."""

    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=20)
    financing_preference: str | None = None

    @field_validator("phone", "address", "city", "state", "pincode")
    @classmethod
    def fields_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Field must not be blank if supplied")
        return value


class BuyerProfileResponse(BaseModel):
    """Representation of a Bulk Buyer profile."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    phone: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    financing_preference: str
    created_at: datetime
    updated_at: datetime