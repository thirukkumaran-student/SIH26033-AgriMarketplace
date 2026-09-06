from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FinancingRelationship(Base):
    __tablename__ = "financing_relationships"

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(nullable=False)
    financier_id: Mapped[int] = mapped_column(nullable=False)

    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    tenure_days: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )


class FinancingRequest(Base):
    __tablename__ = "financing_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    buyer_id: Mapped[int] = mapped_column(nullable=False)
    financier_id: Mapped[int] = mapped_column(nullable=False)

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

    tenure_days: Mapped[int] = mapped_column(nullable=False)

class FinancingTransaction(Base):
    __tablename__ = "financing_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    relationship_id: Mapped[int] = mapped_column(nullable=False)
    order_id: Mapped[int] = mapped_column(nullable=False)

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

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )