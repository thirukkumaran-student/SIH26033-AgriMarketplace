"""Shipment ORM model.

Represents a shipment created by a FARMER after an order is confirmed.
P5 (Logistics) will later integrate with this model for route optimization
and actual shipment processing. For now, the model provides the farmer-facing
view of shipment status.

Relationship chain: Shipment -> Order -> Produce -> Farmer (User)
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Numeric, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.order import Order
from app.core.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING"
    )  # PENDING / ASSIGNED / PICKED_UP / IN_TRANSIT / DELIVERED / CANCELLED
    pickup_location: Mapped[str] = mapped_column(String(500), nullable=False)
    destination: Mapped[str] = mapped_column(String(500), nullable=False)
    estimated_delivery: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    logistics_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    logistics_fee_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="DUE", server_default="DUE"
    )
    logistics_fee_reference: Mapped[str | None] = mapped_column(String(30), nullable=True)
    logistics_fee_collected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ORM relationship: a shipment belongs to one order
    order: Mapped["Order"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<Shipment id={self.id} order_id={self.order_id} "
            f"status={self.status!r}>"
        )
