"""Dispute ORM model.

Represents a dispute raised by a CONSUMER against an Order.
Admins can resolve disputes through the resolution workflow.

Relationship chain: Dispute -> Order -> Produce / Buyer
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raised_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="OPEN"
    )  # OPEN / ACCEPTED / REJECTED / PARTIAL
    resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    admin_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ORM relationships
    order: Mapped["Order"] = relationship()
    raised_by_user: Mapped["User"] = relationship(foreign_keys=[raised_by])
    resolved_by_user: Mapped["User"] = relationship(foreign_keys=[resolved_by])

    def __repr__(self) -> str:
        return (
            f"<Dispute id={self.id} order_id={self.order_id} "
            f"raised_by={self.raised_by} status={self.status!r}>"
        )
