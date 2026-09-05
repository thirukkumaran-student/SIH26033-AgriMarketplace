"""Shared enums used across the whole application."""

from enum import Enum


class Role(str, Enum):
    """The roles supported by the platform.

    There is exactly ONE users table and every user carries one of these
    roles. New feature modules (Farmer, Consumer, Marketplace, ...) reuse
    these values instead of defining their own.
    """

    FARMER = "FARMER"
    CONSUMER = "CONSUMER"
    BULK_BUYER = "BULK_BUYER"
    FINANCIER = "FINANCIER"
    LOGISTICS = "LOGISTICS"
    ADMIN = "ADMIN"


class VerificationStatus(str, Enum):
    """Status of a farmer's verification document submission."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ProduceStatus(str, Enum):
    """Status of a produce listing."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SOLD_OUT = "SOLD_OUT"


class OrderStatus(str, Enum):
    """Status of an order."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ShipmentStatus(str, Enum):
    """Status of a farmer shipment."""

    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
