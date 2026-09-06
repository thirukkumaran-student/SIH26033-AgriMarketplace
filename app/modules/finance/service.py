from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.modules.finance.models import (
    FinancingRelationship,
    FinancingRequest,
    FinancingTransaction,
)

from app.modules.finance.schemas import (
    FinancingRelationshipCreate,
    FinancingRequestCreate,
    FinancingDecision,
    FinancingTransactionCreate,
)

def create_relationship(
    db: Session,
    data: FinancingRelationshipCreate,
) -> FinancingRelationship:
    relationship = FinancingRelationship(
        buyer_id=data.buyer_id,
        financier_id=data.financier_id,
        credit_limit=data.credit_limit,
        interest_rate=data.interest_rate,
        tenure_days=data.tenure_days,
        status="ACTIVE",
    )

    db.add(relationship)
    db.commit()
    db.refresh(relationship)

    return relationship


def get_relationships_for_financier(
    db: Session,
    financier_id: int,
) -> list[FinancingRelationship]:
    return (
        db.query(FinancingRelationship)
        .filter(FinancingRelationship.financier_id == financier_id)
        .all()
    )

def get_relationships_for_buyer(
    db: Session,
    buyer_id: int,
) -> list[FinancingRelationship]:
    return (
        db.query(FinancingRelationship)
        .filter(FinancingRelationship.buyer_id == buyer_id)
        .all()
    )


def create_financing_request(
    db: Session,
    data: FinancingRequestCreate,
    buyer_id: int,
) -> FinancingRequest:
    request = FinancingRequest(
        buyer_id=buyer_id,
        financier_id=data.financier_id,
        status="PENDING",
        credit_limit=Decimal("0.00"),
        interest_rate=Decimal("0.00"),
        tenure_days=0,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def get_financing_requests_for_financier(
    db: Session,
    financier_id: int,
) -> list[FinancingRequest]:
    return (
        db.query(FinancingRequest)
        .filter(FinancingRequest.financier_id == financier_id)
        .all()
    )

def get_financing_requests_for_buyer(
    db: Session,
    buyer_id: int,
) -> list[FinancingRequest]:
    return (
        db.query(FinancingRequest)
        .filter(FinancingRequest.buyer_id == buyer_id)
        .all()
    )


def approve_financing_request(
    db: Session,
    request_id: int,
    decision: FinancingDecision,
) -> FinancingRequest:
    request = (
        db.query(FinancingRequest)
        .filter(FinancingRequest.id == request_id)
        .first()
    )

    if request is None:
        raise ValueError("Financing request not found")

    if request.status != "PENDING":
        raise ValueError("Financing request is no longer pending")

    request.credit_limit = decision.credit_limit
    request.interest_rate = decision.interest_rate
    request.tenure_days = decision.tenure_days
    request.status = "APPROVED"

    db.commit()
    db.refresh(request)

    return request


def reject_financing_request(
    db: Session,
    request_id: int,
) -> FinancingRequest:
    request = (
        db.query(FinancingRequest)
        .filter(FinancingRequest.id == request_id)
        .first()
    )

    if request is None:
        raise ValueError("Financing request not found")

    if request.status != "PENDING":
        raise ValueError("Financing request is no longer pending")

    request.status = "REJECTED"

    db.commit()
    db.refresh(request)

    return request

def select_financing_offer(
    db: Session,
    request_id: int,
) -> FinancingRelationship:
    request = (
        db.query(FinancingRequest)
        .filter(FinancingRequest.id == request_id)
        .first()
    )

    if request is None:
        raise ValueError("Financing request not found")

    if request.status != "APPROVED":
        raise ValueError(
            "Only an approved financing offer can be selected"
        )

    relationship = FinancingRelationship(
        buyer_id=request.buyer_id,
        financier_id=request.financier_id,
        credit_limit=request.credit_limit,
        interest_rate=request.interest_rate,
        tenure_days=request.tenure_days,
        status="ACTIVE",
    )

    request.status = "SELECTED"

    db.add(relationship)
    db.commit()
    db.refresh(relationship)

    return relationship

def create_financing_transaction(
    db: Session,
    data: FinancingTransactionCreate,
) -> FinancingTransaction:
    relationship = (
        db.query(FinancingRelationship)
        .filter(FinancingRelationship.id == data.relationship_id)
        .first()
    )

    if relationship is None:
        raise ValueError("Financing relationship not found")

    if relationship.status != "ACTIVE":
        raise ValueError("Financing relationship is not active")

    transactions = (
        db.query(FinancingTransaction)
        .filter(FinancingTransaction.relationship_id == relationship.id)
        .all()
    )

    outstanding_principal = sum(
        (
            transaction.principal
            for transaction in transactions
            if transaction.status == "ACTIVE"
        ),
        Decimal("0.00"),
    )

    available_credit = relationship.credit_limit - outstanding_principal

    if data.principal > available_credit:
        raise ValueError("Insufficient financing capacity")

    transaction = FinancingTransaction(
        relationship_id=relationship.id,
        order_id=data.order_id,
        principal=data.principal,
        interest=Decimal("0.00"),
        total_repayment=Decimal("0.00"),
        status="ACTIVE",
    )

    db.add(transaction)
    db.flush()

    return transaction

def get_financing_transactions(
    db: Session,
    relationship_id: int,
) -> list[FinancingTransaction]:
    return (
        db.query(FinancingTransaction)
        .filter(
            FinancingTransaction.relationship_id
            == relationship_id
        )
        .all()
    )

def get_financing_transaction(
    db: Session,
    transaction_id: int,
) -> FinancingTransaction:

    transaction = (
        db.query(FinancingTransaction)
        .filter(FinancingTransaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise ValueError("Financing transaction not found")

    return transaction

def calculate_interest(
    principal: Decimal,
    annual_rate: Decimal,
    days: int,
) -> Decimal:

    interest = (
        principal
        * annual_rate
        * Decimal(days)
        / Decimal("365")
        / Decimal("100")
    )

    return interest.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

def repay_financing_transaction(
    db: Session,
    transaction_id: int,
) -> FinancingTransaction:

    transaction = (
        db.query(FinancingTransaction)
        .filter(FinancingTransaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise ValueError("Financing transaction not found")

    if transaction.status != "ACTIVE":
        raise ValueError("Financing transaction is not active")

    relationship = (
        db.query(FinancingRelationship)
        .filter(
            FinancingRelationship.id == transaction.relationship_id
        )
        .first()
    )

    if relationship is None:
        raise ValueError("Financing relationship not found")

    interest = calculate_interest(
        transaction.principal,
        relationship.interest_rate,
        relationship.tenure_days,
    )

    total_repayment = (
        transaction.principal + interest
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    transaction.interest = interest
    transaction.total_repayment = total_repayment
    transaction.status = "COMPLETED"

    db.commit()
    db.refresh(transaction)

    return transaction