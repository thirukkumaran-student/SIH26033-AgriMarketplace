"""Pydantic schemas for Admin Verification endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import VerificationStatus


class AdminRejectRequest(BaseModel):
    """Payload for POST /api/admin/verifications/{user_id}/reject."""

    remarks: str = Field(
        min_length=1,
        max_length=2000,
        description="Rejection reason (required)",
    )


class AdminVerificationDocumentResponse(BaseModel):
    """A single verification document seen by the admin."""

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


class AdminFarmerProfileResponse(BaseModel):
    """Farmer profile information for the admin review view."""

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


class AdminVerificationDetailResponse(BaseModel):
    """Full farmer verification details for admin review."""

    user_id: int
    applicant_name: str
    farmer_email: str
    overall_status: str
    profile: AdminFarmerProfileResponse | None
    documents: list[AdminVerificationDocumentResponse]


class AdminVerificationQueueItem(BaseModel):
    """One item in the admin's verification queue."""

    user_id: int
    applicant_name: str
    farmer_email: str
    overall_status: str
    document_count: int
    earliest_submission: datetime


class AdminActionResponse(BaseModel):
    """Response after approve / reject action."""

    user_id: int
    applicant_name: str
    action: str
    new_status: VerificationStatus
    reviewed_by: int
    reviewed_at: datetime
    documents_updated: int
    remarks: str | None = None


class MonitoringDatabase(BaseModel):
    """Database connectivity status for the monitoring endpoint.

    Only exposes a safe status string and a boolean error flag — never the
    underlying connection string or exception details.
    """

    status: str  # "connected" | "unavailable"
    error: bool = False


class MonitoringResponse(BaseModel):
    """Response body for GET /api/admin/monitoring.

    Deliberately exposes NO secrets: no DB URL, credentials, JWT secrets,
    .env contents, or private user data.
    """

    application: str
    version: str
    status: str  # "ok" | "degraded"
    timestamp: datetime
    database: MonitoringDatabase
