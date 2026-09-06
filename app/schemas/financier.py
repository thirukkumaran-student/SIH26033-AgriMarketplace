from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FinancierProfileCreate(BaseModel):
    institution_name: str = Field(min_length=1, max_length=200)
    institution_type: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=20)

    @field_validator(
        "institution_name",
        "institution_type",
        "phone",
        "address",
        "city",
        "state",
        "pincode",
    )
    @classmethod
    def reject_blank_strings(cls, value):
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value


class FinancierProfileUpdate(BaseModel):
    institution_name: str | None = Field(default=None, min_length=1, max_length=200)
    institution_type: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=20)

    @field_validator(
        "institution_name",
        "institution_type",
        "phone",
        "address",
        "city",
        "state",
        "pincode",
    )
    @classmethod
    def reject_blank_strings(cls, value):
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value


class FinancierProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    institution_name: str
    institution_type: str | None
    phone: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    created_at: datetime
    updated_at: datetime