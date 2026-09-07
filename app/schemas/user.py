"""Pydantic schemas for user / auth payloads and responses.

Schemas define what the API accepts and returns. The ``password_hash``
column is deliberately NOT part of any response schema, so it can never
leak into an API response.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.enums import Role


class UserRegister(BaseModel):
    """Payload for POST /api/auth/register."""

    name: str = Field(min_length=1, max_length=100, description="User's display name")
    email: EmailStr = Field(description="Valid email address")
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
    def normalize_email(cls, value: str) -> str:
        """Normalize: trim whitespace and lowercase the whole address."""
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, value: str) -> str:
        # bcrypt only considers the first 72 BYTES; check bytes, not characters,
        # so multi-byte (unicode) passwords get a clear validation error.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long for bcrypt")
        return value


class LoginRequest(BaseModel):
    """Payload for POST /api/auth/login."""

    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserPublic(BaseModel):
    """Safe user information returned by the API. Never includes hashes."""

    model_config = ConfigDict(from_attributes=True)  # allow User ORM -> schema

    id: int
    name: str
    email: EmailStr
    role: Role
    created_at: datetime


class TokenResponse(BaseModel):
    """Response of POST /api/auth/login."""

    access_token: str
    token_type: str = "bearer"
    user: UserPublic
