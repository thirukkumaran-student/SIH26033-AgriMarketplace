"""Database integrity tests for the finance module."""

from decimal import Decimal

import pytest

from app.core.database import SessionLocal
from app.models.order import Order
from app.models.user import User
from app.modules.finance.models import (
    FinancingRelationship,
    FinancingTransaction,
)


def test_financing_transaction_requires_existing_relationship():
    """A transaction cannot reference a non-existent relationship."""
    from decimal import Decimal

    import pytest

    from app.modules.finance.schemas import FinancingTransactionCreate
    from app.modules.finance.service import create_financing_transaction

    db = SessionLocal()

    try:
        data = FinancingTransactionCreate(
            relationship_id=99999,
            order_id=99999,
            principal=Decimal("100.00"),
        )

        with pytest.raises(ValueError, match="Financing relationship not found"):
            create_financing_transaction(db, data)

    finally:
        db.close()

def test_financing_transaction_requires_existing_order():
    """A transaction cannot reference a non-existent order."""
    db = SessionLocal()

    try:
        buyer = User(
            name="Buyer",
            email="finance_integrity_buyer_2@example.com",
            password_hash="test-hash",
            role="BULK_BUYER",
        )

        financier = User(
            name="Financier",
            email="finance_integrity_financier@example.com",
            password_hash="test-hash",
            role="FINANCIER",
        )

        db.add_all([buyer, financier])
        db.flush()

        relationship = FinancingRelationship(
            buyer_id=buyer.id,
            financier_id=financier.id,
            credit_limit=Decimal("1000.00"),
            interest_rate=Decimal("10.00"),
            tenure_days=30,
            status="ACTIVE",
        )

        db.add(relationship)
        db.flush()

        transaction = FinancingTransaction(
            relationship_id=relationship.id,
            order_id=999999,
            principal=Decimal("10.00"),
            interest=Decimal("0.00"),
            total_repayment=Decimal("0.00"),
            status="ACTIVE",
        )

        db.add(transaction)

        with pytest.raises(Exception):
            db.flush()

        db.rollback()

    finally:
        db.close()