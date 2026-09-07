from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.user import User
from app.modules.auth.dependencies import require_role
from app.modules.finance.models import (
    FinancingRelationship,
    FinancingRequest,
    FinancingTransaction,
)
from app.modules.finance.schemas import (
    FinancingDecision,
    FinancingRequestCreate,
    FinancingRequestResponse,
    FinancingRelationshipResponse,
    FinancingTransactionCreate,
    FinancingTransactionResponse,
)
from app.modules.finance.service import (
    approve_financing_request,
    create_financing_request,
    create_financing_transaction,
    get_financing_requests_for_financier,
    get_financing_transaction,
    get_financing_transactions,
    get_relationships_for_buyer,
    get_relationships_for_financier,
    reject_financing_request,
    repay_financing_transaction,
    select_financing_offer,
    get_financing_requests_for_buyer,
)

from app.models.order import Order

router = APIRouter(
    prefix="/api/finance",
    tags=["Finance"],
)


@router.get(
    "/relationships/me",
    response_model=list[FinancingRelationshipResponse],
)
def get_my_financing_relationships(
    current_user: User = Depends(
        require_role(Role.BULK_BUYER, Role.FINANCIER)
    ),
    db: Session = Depends(get_db),
):
    if current_user.role == Role.BULK_BUYER.value:
        return get_relationships_for_buyer(
            db,
            current_user.id,
        )

    return get_relationships_for_financier(
        db,
        current_user.id,
    )


@router.post(
    "/requests",
    response_model=FinancingRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_request(
    data: FinancingRequestCreate,
    current_user: User = Depends(require_role(Role.BULK_BUYER)),
    db: Session = Depends(get_db),
):
    return create_financing_request(
        db,
        data,
        current_user.id,
    )


@router.get(
    "/requests",
    response_model=list[FinancingRequestResponse],
)
def get_financing_requests(
    current_user: User = Depends(
        require_role(Role.FINANCIER, Role.BULK_BUYER)
    ),
    db: Session = Depends(get_db),
):
    if current_user.role == Role.BULK_BUYER.value:
        return get_financing_requests_for_buyer(db, current_user.id)

    return get_financing_requests_for_financier(db, current_user.id)


@router.post(
    "/requests/{request_id}/approve",
    response_model=FinancingRequestResponse,
)
def approve_request(
    request_id: int,
    decision: FinancingDecision,
    current_user: User = Depends(require_role(Role.FINANCIER)),
    db: Session = Depends(get_db),
):
    request = (
        db.query(FinancingRequest)
        .filter(FinancingRequest.id == request_id)
        .first()
    )

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing request not found",
        )

    if request.financier_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to manage this financing request",
        )

    try:
        return approve_financing_request(
            db,
            request_id,
            decision,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/requests/{request_id}/reject",
    response_model=FinancingRequestResponse,
)
def reject_request(
    request_id: int,
    current_user: User = Depends(require_role(Role.FINANCIER)),
    db: Session = Depends(get_db),
):
    request = (
        db.query(FinancingRequest)
        .filter(FinancingRequest.id == request_id)
        .first()
    )

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing request not found",
        )

    if request.financier_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to manage this financing request",
        )

    try:
        return reject_financing_request(
            db,
            request_id,
        )
    except ValueError as exc:
        detail = str(exc)

        if detail == "Financing request not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


@router.post(
    "/requests/{request_id}/select",
    response_model=FinancingRelationshipResponse,
)
def select_offer(
    request_id: int,
    current_user: User = Depends(require_role(Role.BULK_BUYER)),
    db: Session = Depends(get_db),
):
    request = (
        db.query(FinancingRequest)
        .filter(FinancingRequest.id == request_id)
        .first()
    )

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing request not found",
        )

    if request.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to select this financing offer",
        )

    try:
        return select_financing_offer(
            db,
            request_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/transactions",
    response_model=FinancingTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    data: FinancingTransactionCreate,
    current_user: User = Depends(require_role(Role.BULK_BUYER)),
    db: Session = Depends(get_db),
):
    relationship = (
        db.query(FinancingRelationship)
        .filter(
            FinancingRelationship.id == data.relationship_id
        )
        .first()
    )

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing relationship not found",
        )

    if relationship.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to use this financing relationship",
        )

    order = db.scalar(
        select(Order).where(Order.id == data.order_id)
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to finance this order",
        )

    existing_transaction = db.scalar(
        select(FinancingTransaction).where(
            FinancingTransaction.order_id == data.order_id
        )
    )

    if existing_transaction is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order already has a financing transaction",
        )

    try:
        transaction = create_financing_transaction(db, data)
        db.commit()
        db.refresh(transaction)
        return transaction
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/transactions",
    response_model=list[FinancingTransactionResponse],
)
def get_transactions(
    relationship_id: int,
    current_user: User = Depends(require_role(Role.BULK_BUYER)),
    db: Session = Depends(get_db),
):
    relationship = (
        db.query(FinancingRelationship)
        .filter(
            FinancingRelationship.id == relationship_id
        )
        .first()
    )

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing relationship not found",
        )

    if relationship.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this financing relationship",
        )

    return get_financing_transactions(
        db,
        relationship_id,
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=FinancingTransactionResponse,
)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(require_role(Role.BULK_BUYER)),
    db: Session = Depends(get_db),
):
    try:
        transaction = get_financing_transaction(
            db,
            transaction_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    relationship = (
        db.query(FinancingRelationship)
        .filter(
            FinancingRelationship.id == transaction.relationship_id
        )
        .first()
    )

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing relationship not found",
        )

    if relationship.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this transaction",
        )

    return transaction


@router.post(
    "/transactions/{transaction_id}/repayment",
    response_model=FinancingTransactionResponse,
)
def repay_transaction(
    transaction_id: int,
    current_user: User = Depends(require_role(Role.BULK_BUYER)),
    db: Session = Depends(get_db),
):
    try:
        transaction = get_financing_transaction(
            db,
            transaction_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    relationship = (
        db.query(FinancingRelationship)
        .filter(
            FinancingRelationship.id == transaction.relationship_id
        )
        .first()
    )

    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financing relationship not found",
        )

    if relationship.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to repay this transaction",
        )

    try:
        return repay_financing_transaction(
            db,
            transaction_id,
        )
    except ValueError as exc:
        detail = str(exc)

        if detail in {
            "Financing transaction not found",
            "Financing relationship not found",
        }:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )