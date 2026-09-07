from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Handoff(Base):
    __tablename__ = "handoffs"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(
        Integer,
        ForeignKey("shipments.id"),
        nullable=False,
        index=True,
    )

    from_party = Column(String, nullable=False)
    to_party = Column(String, nullable=False)
    location = Column(String, nullable=False)
    remarks = Column(String, nullable=True)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )