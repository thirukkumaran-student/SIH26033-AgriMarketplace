"""Finance ORM models.

Financing relationships are long-lived agreements between a bulk buyer and
financier. Financing transactions are order-specific financing events.

All cross-module identifiers are backed by database foreign keys so finance
cannot contain references to non-existent users, relationships, or orders.
"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FinancingRelationship(Base):
    __tablename__ = "financing_relationships"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    financier_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    tenure_days: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )


class FinancingRequest(Base):
    __tablename__ = "financing_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    financier_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    tenure_days: Mapped[int] = mapped_column(
        nullable=False,
    )


class FinancingTransaction(Base):
    __tablename__ = "financing_transactions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    relationship_id: Mapped[int] = mapped_column(
        ForeignKey(
            "financing_relationships.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    principal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    interest: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    total_repayment: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    # ACTIVE   -> financing is outstanding
    # COMPLETED -> financing has been repaid
    # VOIDED   -> financed order was cancelled before repayment
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )