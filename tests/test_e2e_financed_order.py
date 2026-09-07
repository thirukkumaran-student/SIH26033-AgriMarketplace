"""End-to-end tests for the financed bulk-buyer procurement flow."""

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.modules.finance.models import FinancingRelationship, FinancingTransaction
from tests.test_auth import auth_headers, obtain_token, register_user


def get_user_id(email: str) -> int:
    """Return the database ID for a registered user."""
    db = SessionLocal()
    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )
        assert user is not None
        return user.id
    finally:
        db.close()


def register_farmer_with_produce(
    client: TestClient,
    email: str = "e2e_farmer@example.com",
) -> tuple[str, dict]:
    """Register, verify, approve and create produce for a farmer."""
    register_user(
        client,
        email=email,
        name="E2E Farmer",
        role="FARMER",
    )
    farmer_token = obtain_token(client, email=email)

    for document_type in ["AADHAAR", "PAN"]:
        response = client.post(
            "/api/verification/documents",
            headers=auth_headers(farmer_token),
            json={
                "document_type": document_type,
                "document_number": f"E2E-{document_type}",
            },
        )
        assert response.status_code == 201, response.text

    register_user(
        client,
        email="e2e_admin@example.com",
        name="E2E Admin",
        role="ADMIN",
    )
    admin_token = obtain_token(
        client,
        email="e2e_admin@example.com",
    )

    farmer_id = get_user_id(email)

    response = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text

    response = client.post(
        "/api/produce",
        headers=auth_headers(farmer_token),
        json={
            "crop": "Wheat",
            "category": "Cereals",
            "quantity": 100,
            "unit": "kg",
            "price_per_unit": 25.0,
            "location": "E2E Farm",
            "harvest_date": "2026-03-01",
            "quality_grade": "A",
        },
    )
    assert response.status_code == 201, response.text

    return farmer_token, response.json()


def register_and_approve_financier(
    client: TestClient,
    email: str = "e2e_financier@example.com",
) -> tuple[str, int]:
    """Register, verify and approve a financier."""
    register_user(
        client,
        email=email,
        name="E2E Financier",
        role="FINANCIER",
    )
    financier_token = obtain_token(client, email=email)

    response = client.post(
        "/api/financier/profile",
        headers=auth_headers(financier_token),
        json={
            "institution_name": "E2E Finance Ltd",
            "institution_type": "NBFC",
            "phone": "9876543210",
            "address": "Finance Street",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001",
        },
    )
    assert response.status_code == 201, response.text

    response = client.post(
        "/api/verification/documents",
        headers=auth_headers(financier_token),
        json={
            "document_type": "REGISTRATION_CERTIFICATE",
            "document_number": "E2E-FIN-DOC-001",
        },
    )
    assert response.status_code == 201, response.text

    admin_token = obtain_token(
        client,
        email="e2e_admin@example.com",
    )
    financier_id = get_user_id(email)

    response = client.post(
        f"/api/admin/verifications/{financier_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text

    return financier_token, financier_id


def register_buyer(
    client: TestClient,
    email: str = "e2e_buyer@example.com",
) -> tuple[str, int]:
    """Register a bulk buyer with platform financing enabled."""
    register_user(
        client,
        email=email,
        name="E2E Bulk Buyer",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(client, email=email)

    response = client.post(
        "/api/buyer/profile",
        headers=auth_headers(buyer_token),
        json={
            "phone": "9876543210",
            "address": "Buyer Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "financing_preference": "PLATFORM",
        },
    )
    assert response.status_code == 201, response.text

    return buyer_token, get_user_id(email)


def establish_financing_relationship(
    client: TestClient,
    buyer_token: str,
    financier_token: str,
    financier_id: int,
) -> int:
    """Discover a financier, request financing, approve it and select the offer."""
    response = client.get(
        "/api/financier/",
        headers=auth_headers(buyer_token),
    )
    assert response.status_code == 200, response.text

    financiers = response.json()
    assert any(
        financier["user_id"] == financier_id
        for financier in financiers
    )

    response = client.post(
        "/api/finance/requests",
        headers=auth_headers(buyer_token),
        json={
            "financier_id": financier_id,
        },
    )
    assert response.status_code == 201, response.text

    request = response.json()
    request_id = request["id"]

    response = client.post(
        f"/api/finance/requests/{request_id}/approve",
        headers=auth_headers(financier_token),
        json={
            "credit_limit": 1000,
            "interest_rate": 10,
            "tenure_days": 90,
        },
    )
    assert response.status_code == 200, response.text

    assert response.json()["status"] == "APPROVED"

    response = client.post(
        f"/api/finance/requests/{request_id}/select",
        headers=auth_headers(buyer_token),
    )
    assert response.status_code == 200, response.text

    relationship = response.json()

    assert relationship["status"] == "ACTIVE"
    assert relationship["buyer_id"] > 0
    assert relationship["financier_id"] == financier_id

    return relationship["id"]


def test_e2e_financed_order_and_repayment(client: TestClient):
    """Prove the complete farmer-to-financed-order-to-repayment flow."""
    _, produce = register_farmer_with_produce(client)

    # Marketplace must expose the approved farmer's active produce.
    register_user(
        client,
        email="e2e_marketplace_buyer@example.com",
        name="Marketplace Buyer",
        role="BULK_BUYER",
    )
    marketplace_buyer_token = obtain_token(
        client,
        email="e2e_marketplace_buyer@example.com",
    )

    response = client.get(
        "/api/marketplace/produce",
        headers=auth_headers(marketplace_buyer_token),
    )
    assert response.status_code == 200, response.text

    marketplace_items = response.json()
    assert any(item["id"] == produce["id"] for item in marketplace_items)

    # Register and approve financier.
    financier_token, financier_id = register_and_approve_financier(client)

    # Approved financier must become discoverable.
    buyer_token, buyer_id = register_buyer(client)

    response = client.get(
        "/api/financier/",
        headers=auth_headers(buyer_token),
    )
    assert response.status_code == 200, response.text
    assert any(
        item["user_id"] == financier_id
        for item in response.json()
    )

    # Buyer requests financing and selects the approved offer.
    relationship_id = establish_financing_relationship(
        client,
        buyer_token,
        financier_token,
        financier_id,
    )

    # Place a financed bulk order.
    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
            "relationship_id": relationship_id,
        },
    )
    assert response.status_code == 201, response.text

    order = response.json()

    assert order["buyer_id"] == buyer_id
    assert order["produce_id"] == produce["id"]
    assert order["quantity"] == 10
    assert order["total_amount"] == "250.00"

    # Confirm the order-specific financing transaction exists.
    db = SessionLocal()
    try:
        transaction = db.scalar(
            select(FinancingTransaction).where(
                FinancingTransaction.order_id == order["id"]
            )
        )

        assert transaction is not None
        assert transaction.relationship_id == relationship_id
        assert transaction.principal == Decimal("250.00")
        assert transaction.status == "ACTIVE"
    finally:
        db.close()

    transaction_id = transaction.id

    # Repay through the real API.
    response = client.post(
        f"/api/finance/transactions/{transaction_id}/repayment",
        headers=auth_headers(buyer_token),
    )
    assert response.status_code == 200, response.text

    repayment = response.json()

    assert repayment["status"] == "COMPLETED"
    assert repayment["principal"] == "250.00"
    assert repayment["interest"] == "6.16"
    assert repayment["total_repayment"] == "256.16"


def test_relationship_supports_two_orders_within_capacity(
    client: TestClient,
):
    """One ACTIVE relationship can finance multiple orders within its limit."""
    _, produce = register_farmer_with_produce(
        client,
        email="reuse_farmer@example.com",
    )

    financier_token, financier_id = register_and_approve_financier(
        client,
        email="reuse_financier@example.com",
    )

    buyer_token, _ = register_buyer(
        client,
        email="reuse_buyer@example.com",
    )

    relationship_id = establish_financing_relationship(
        client,
        buyer_token,
        financier_token,
        financier_id,
    )

    # First order: 20 × ₹25 = ₹500.
    first_response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
            "relationship_id": relationship_id,
        },
    )
    assert first_response.status_code == 201, first_response.text

    # Second order: another ₹500 against the same ₹1,000 relationship.
    second_response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
            "relationship_id": relationship_id,
        },
    )
    assert second_response.status_code == 201, second_response.text

    first_order_id = first_response.json()["id"]
    second_order_id = second_response.json()["id"]

    assert first_order_id != second_order_id

    db = SessionLocal()
    try:
        transactions = list(
            db.scalars(
                select(FinancingTransaction).where(
                    FinancingTransaction.relationship_id == relationship_id
                )
            ).all()
        )

        assert len(transactions) == 2
        assert {
            transaction.order_id
            for transaction in transactions
        } == {
            first_order_id,
            second_order_id,
        }

        assert sum(
            transaction.principal
            for transaction in transactions
            if transaction.status == "ACTIVE"
        ) == Decimal("1000.00")
    finally:
        db.close()


def test_repayment_calculates_interest_correctly(client: TestClient):
    """Repayment uses the agreed annual simple-interest calculation."""
    _, produce = register_farmer_with_produce(
        client,
        email="repayment_farmer@example.com",
    )

    financier_token, financier_id = register_and_approve_financier(
        client,
        email="repayment_financier@example.com",
    )

    buyer_token, _ = register_buyer(
        client,
        email="repayment_buyer@example.com",
    )

    relationship_id = establish_financing_relationship(
        client,
        buyer_token,
        financier_token,
        financier_id,
    )

    # ₹250 principal, 10% annual rate, 90-day tenure.
    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
            "relationship_id": relationship_id,
        },
    )
    assert response.status_code == 201, response.text

    order_id = response.json()["id"]

    db = SessionLocal()
    try:
        transaction = db.scalar(
            select(FinancingTransaction).where(
                FinancingTransaction.order_id == order_id
            )
        )
        assert transaction is not None
        transaction_id = transaction.id
    finally:
        db.close()

    response = client.post(
        f"/api/finance/transactions/{transaction_id}/repayment",
        headers=auth_headers(buyer_token),
    )
    assert response.status_code == 200, response.text

    repayment = response.json()

    assert Decimal(repayment["principal"]) == Decimal("250.00")
    assert Decimal(repayment["interest"]) == Decimal("6.16")
    assert Decimal(repayment["total_repayment"]) == Decimal("256.16")
    assert repayment["status"] == "COMPLETED"