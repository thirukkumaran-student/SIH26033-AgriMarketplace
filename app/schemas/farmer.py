"""Pydantic schemas for Farmer Profile and Verification Document payloads.

These schemas define what the API accepts and returns.  They deliberately
exclude the ``user_id`` from input — it is taken from the authenticated
JWT instead.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import VerificationStatus

# ---------------------------------------------------------------------------
# Farmer Profile
# ---------------------------------------------------------------------------


class FarmerProfileCreate(BaseModel):
    """Payload for POST /api/farmer/profile (create own profile)."""

    phone: str | None = Field(default=None, max_length=20, description="Contact number")
    farm_name: str | None = Field(default=None, max_length=200, description="Name of the farm")
    farm_size_acres: float | None = Field(
        default=None, ge=0, description="Farm size in acres"
    )
    farm_location: str | None = Field(default=None, max_length=500, description="Full address")
    soil_type: str | None = Field(default=None, max_length=100, description="Primary soil type")
    irrigation_type: str | None = Field(
        default=None, max_length=100, description="Primary irrigation method"
    )
    bank_account_number: str | None = Field(default=None, max_length=30)
    ifsc_code: str | None = Field(default=None, max_length=20)


class FarmerProfileUpdate(BaseModel):
    """Payload for PUT /api/farmer/profile (update own profile).

    All fields optional — only provided fields are overwritten.
    """

    phone: str | None = Field(default=None, max_length=20)
    farm_name: str | None = Field(default=None, max_length=200)
    farm_size_acres: float | None = Field(default=None, ge=0)
    farm_location: str | None = Field(default=None, max_length=500)
    soil_type: str | None = Field(default=None, max_length=100)
    irrigation_type: str | None = Field(default=None, max_length=100)
    bank_account_number: str | None = Field(default=None, max_length=30)
    ifsc_code: str | None = Field(default=None, max_length=20)


class FarmerProfileResponse(BaseModel):
    """Public representation of a farmer profile."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    phone: str | None
    farm_name: str | None
    farm_size_acres: float | None
    farm_location: str | None
    soil_type: str | None
    irrigation_type: str | None
    bank_account_number: str | None
    ifsc_code: str | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Verification Documents
# ---------------------------------------------------------------------------


class VerificationDocumentSubmit(BaseModel):
    """Payload for POST /api/verification/documents."""

    document_type: str = Field(
        min_length=1,
        max_length=50,
        description="Type of document (e.g. AADHAAR, PAN, LAND_RECORD)",
    )
    document_number: str = Field(
        min_length=1,
        max_length=100,
        description="Document identifier / number",
    )
    file_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL or path to the uploaded document file (optional)",
    )


class VerificationDocumentResponse(BaseModel):
    """Representation of a verification document submission."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    document_type: str
    document_number: str
    file_url: str | None
    status: VerificationStatus
    remarks: str | None
    reviewed_by: int | None
    submitted_at: datetime
    reviewed_at: datetime | None


class VerificationStatusResponse(BaseModel):
    """Summary of the farmer's overall verification state."""

    farmer_name: str
    user_id: int
    documents: list[VerificationDocumentResponse]
    overall_status: str
