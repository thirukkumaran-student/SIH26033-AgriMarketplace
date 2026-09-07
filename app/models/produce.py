"""Produce ORM model.

Represents a produce listing created by a verified FARMER.
This is the SINGLE SOURCE OF TRUTH for produce data — the Marketplace,
Consumer, and other modules will read from this table.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Produce(Base):
    __tablename__ = "produce"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    crop: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)  # kg, quintal, ton, etc.
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    harvest_date: Mapped[date | None] = mapped_column(nullable=True)
    quality_grade: Mapped[str | None] = mapped_column(String(20), nullable=True)  # A, B, C, Premium
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ACTIVE"
    )  # ACTIVE / INACTIVE / SOLD_OUT
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ORM relationship
    farmer: Mapped["User"] = relationship(foreign_keys=[farmer_id])

    def __repr__(self) -> str:
        return (
            f"<Produce id={self.id} crop={self.crop!r} "
            f"farmer_id={self.farmer_id} status={self.status!r}>"
        )
