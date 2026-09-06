"""ORM models.

Importing this package registers every model on ``Base.metadata`` so that
``create_all`` knows about all tables.
"""

from app.models.user import User
from app.models.farmer import FarmerProfile, VerificationDocument
from app.models.produce import Produce
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.consumer import ConsumerProfile
from app.models.dispute import Dispute

__all__ = ["User", "FarmerProfile", "VerificationDocument", "Produce", "Order", "Shipment", "ConsumerProfile", "Dispute"]
