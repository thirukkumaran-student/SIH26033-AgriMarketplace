from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    logistics_partner_id = Column(Integer, nullable=True)

    pickup_location = Column(String, nullable=False)
    delivery_location = Column(String, nullable=False)

    logistics_cost = Column(Float, nullable=False, default=0.0)
    distance = Column(Float, nullable=False, default=0.0)
    route_sequence = Column(String, nullable=True)

    status = Column(String, nullable=False, default="CREATED")

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )