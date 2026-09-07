"""ORM models.

Importing this package registers every model on ``Base.metadata`` so that
``create_all`` knows about all tables.
"""

from app.models.user import User
from app.models.farmer import FarmerProfile, VerificationDocument
from app.models.produce import Produce
from app.models.order import Order
from app.models.shipment import Shipment
from app.models.handoff import Handoff
from app.models.consumer import ConsumerProfile
from app.models.dispute import Dispute
from app.models.buyer import BuyerProfile
from app.models.financier import FinancierProfile
from app.models.forecast import Forecast
from app.modules.finance.models import (
    FinancingRelationship,
    FinancingRequest,
    FinancingTransaction,
)

__all__ = [
    "User",
    "FarmerProfile",
    "VerificationDocument",
    "Produce",
    "Order",
    "Shipment",
    "Handoff",
    "ConsumerProfile",
    "Dispute",
    "BuyerProfile",
    "FinancierProfile",
    "Forecast",
]