"""Order ORM model.

Represents a purchase order placed by a buyer (CONSUMER / BULK_BUYER) for
a produce listing created by a FARMER.

This is the SHARED order system that Consumer, Bulk Buyer, and future modules
will use.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.produce import Produce


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    produce_id: Mapped[int] = mapped_column(
        ForeignKey("produce.id", ondelete="CASCADE"), nullable=False, index=True
    )
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING"
    )  # PENDING / CONFIRMED / CANCELLED / COMPLETED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ORM relationships
    produce: Mapped["Produce"] = relationship(foreign_keys=[produce_id])
    buyer: Mapped["User"] = relationship(
        foreign_keys=[buyer_id], backref="orders_as_buyer"
    )
    farmer: Mapped["User"] = relationship(
        foreign_keys=[farmer_id], backref="orders_as_farmer"
    )

    def __repr__(self) -> str:
        return (
            f"<Order id={self.id} produce_id={self.produce_id} "
            f"buyer_id={self.buyer_id} farmer_id={self.farmer_id} "
            f"status={self.status!r}>"
        )
