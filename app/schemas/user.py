"""Pydantic schemas for user / auth payloads and responses.

Schemas define what the API accepts and returns. The ``password_hash``
column is deliberately NOT part of any response schema, so it can never
leak into an API response.

Registration identifiers are role-specific:
- FARMER  -> phone (required), email (optional)
- CONSUMER / BULK_BUYER / FINANCIER / LOGISTICS / ADMIN -> email (required)

Login accepts a single ``identifier`` (phone for FARMER, email for others)
plus a password.
"""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.enums import Role


def normalize_phone(value: str) -> str:
    """Strip formatting and return a 10-digit Indian mobile number.

    Accepts: "9876543210", "+91 98765 43210", "(987) 654-3210", etc.
    Rejects: wrong length, letters, or a leading zero.
    """
    cleaned = re.sub(r"[^\d]", "", value.strip())
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not cleaned.isdigit() or len(cleaned) != 10:
        raise ValueError("Phone number must be a 10-digit mobile number")
    if cleaned[0] == "0":
        raise ValueError("Phone number must not start with 0")
    return cleaned


class UserRegister(BaseModel):
    """Payload for POST /api/auth/register.

    FARMER requires ``phone`` (``email`` optional). Every other role
    requires ``email`` and must not send ``phone``.
    """

    name: str = Field(min_length=1, max_length=100, description="User's display name")
    email: EmailStr | None = Field(
        default=None, description="Valid email address (optional for FARMER)"
    )
    phone: str | None = Field(
        default=None, description="10-digit mobile number (required for FARMER only)"
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password (min 8 characters). bcrypt supports up to 72 bytes.",
    )
    role: Role = Field(description="One of the supported platform roles")

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be blank")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        """Normalize: trim whitespace and lowercase the whole address."""
        if value is None:
            return None
        return value.strip().lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        """Normalize and validate the phone number (when supplied)."""
        if value is None:
            return None
        return normalize_phone(value)

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, value: str) -> str:
        # bcrypt only considers the first 72 BYTES; check bytes, not characters,
        # so multi-byte (unicode) passwords get a clear validation error.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long for bcrypt")
        return value

    @model_validator(mode="after")
    def validate_identifiers_for_role(self) -> "UserRegister":
        if self.role == Role.FARMER:
            if not self.phone:
                raise ValueError("Phone number is required for FARMER registration")
        else:
            if not self.email:
                raise ValueError(
                    f"Email is required for {self.role.value} registration"
                )
            if self.phone is not None:
                raise ValueError("Phone is only supported for the FARMER role")
        return self


class LoginRequest(BaseModel):
    """Payload for POST /api/auth/login.

    ``identifier`` is the phone number for FARMER accounts and the email
    address for every other role. The backend resolves which one based on
    the identifier format, so the client does NOT send a role.
    """

    identifier: str = Field(min_length=1, description="Phone (FARMER) or email (other roles)")
    password: str = Field(min_length=1)


class UserPublic(BaseModel):
    """Safe user information returned by the API. Never includes hashes.

    ``email`` and ``phone`` are nullable (a farmer may not have an email;
    non-farmers have no phone).
    """

    model_config = ConfigDict(from_attributes=True)  # allow User ORM -> schema

    id: int
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    role: Role
    created_at: datetime


class TokenResponse(BaseModel):
    """Response of POST /api/auth/login."""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic
