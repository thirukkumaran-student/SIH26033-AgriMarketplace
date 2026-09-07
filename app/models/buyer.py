"""Bulk Buyer profile ORM model.

A buyer profile belongs to exactly one existing User with the BULK_BUYER role.
Authentication remains centralized in the shared users table.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    __table_args__ = (
        CheckConstraint(
            "financing_preference IN ('NONE', 'PLATFORM')",
            name="ck_buyer_financing_preference",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    financing_preference: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NONE",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="buyer_profile",
    )

    def __repr__(self) -> str:
        return (
            f"<BuyerProfile id={self.id} user_id={self.user_id} "
            f"financing_preference={self.financing_preference!r}>"
        )