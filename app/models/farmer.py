"""Farmer Profile and Verification Document ORM models.

- ``FarmerProfile``: one-to-one with users (FARMER role only).
- ``VerificationDocument``: documents a farmer submits for verification;
  one farmer may have many submitted documents over time.

Both are linked to users via ``user_id`` (foreign key). No separate auth
is created — the shared users table is reused.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_farmer_profiles_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    farm_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    farm_size_acres: Mapped[float | None] = mapped_column(nullable=True)
    farm_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    irrigation_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_account_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ORM relationship (not used in code, but handy for future joins)
    user: Mapped["User"] = relationship(back_populates="farmer_profile")

    def __repr__(self) -> str:
        return f"<FarmerProfile id={self.id} user_id={self.user_id}>"


class VerificationDocument(Base):
    __tablename__ = "verification_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g. AADHAAR, PAN, LAND_RECORD
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING"
    )  # PENDING / APPROVED / REJECTED
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<VerificationDocument id={self.id} user_id={self.user_id} "
            f"type={self.document_type!r} status={self.status!r}>"
        )
