"""Tests for the Orders module.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from decimal import Decimal

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user
from app.core.database import SessionLocal
from app.models.buyer import BuyerProfile
from app.models.user import User
from app.modules.finance.models import FinancingRelationship, FinancingTransaction
from app.core.security import decode_access_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_farmer_with_produce(
    client: TestClient,
    email: str = "farmer@example.com",
    crop: str = "Wheat",
    quantity: int = 100,
    price_per_unit: float = 25.0,
) -> tuple[str, dict]:
    """Register a farmer, approve them, create a produce listing, return (farmer_token, produce_body)."""
    register_user(client, email=email, role="FARMER")
    farmer_token = obtain_token(client, email=email)

    # Submit verification documents
    for doc_type in ["AADHAAR", "PAN"]:
        resp = client.post(
            "/api/verification/documents",
            headers=auth_headers(farmer_token),
            json={
                "document_type": doc_type,
                "document_number": f"DOC-{doc_type}",
            },
        )
        assert resp.status_code == 201, resp.text

    # Admin approves
    register_user(client, email="admin@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin@example.com")

    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200, resp.text

    body = create_produce(
        client,
        farmer_token,
        crop=crop,
        quantity=quantity,
        price_per_unit=price_per_unit,
    )

    return farmer_token, body


def create_produce(client: TestClient, token: str, **overrides) -> dict:
    """Create a produce listing and return the response body."""
    payload = {
        "crop": "Wheat",
        "category": "Cereals",
        "quantity": 100,
        "unit": "kg",
        "price_per_unit": 25.0,
        "location": "Village Rampur, UP",
        "harvest_date": "2026-03-01",
        "quality_grade": "A",
    }

    payload.update(overrides)

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json=payload,
    )

    return resp.json()


# ---------------------------------------------------------------------------
# Create order — buyer roles
# ---------------------------------------------------------------------------


def test_buyer_can_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert resp.status_code == 201

    body = resp.json()

    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 10
    assert body["unit_price"] == "25.00"
    assert body["total_amount"] == "250.00"
    assert body["status"] == "PENDING"
    assert body["farmer_id"] > 0
    assert body["buyer_id"] > 0


def test_consumer_can_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    assert resp.status_code == 201


def test_bulk_buyer_can_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="buyer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
        },
    )

    assert resp.status_code == 201


def test_farmer_cannot_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(farmer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    assert resp.status_code == 403


def test_unauthenticated_cannot_create_order(client: TestClient):
    resp = client.post(
        "/api/orders",
        json={
            "produce_id": 1,
            "quantity": 1,
        },
    )

    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Create order — business rules
# ---------------------------------------------------------------------------


def test_nonexistent_produce_returns_error(client: TestClient):
    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": 99999,
            "quantity": 10,
        },
    )

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_inactive_produce_cannot_be_ordered(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
    )

    resp = client.patch(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
        json={"status": "INACTIVE"},
    )

    assert resp.status_code == 200

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert resp.status_code == 400
    assert "not available" in resp.json()["detail"].lower()


def test_quantity_must_be_gt_zero(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 0,
        },
    )

    assert resp.status_code == 422


def test_cannot_order_more_than_stock(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=20,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 50,
        },
    )

    assert resp.status_code == 409
    assert "available" in resp.json()["detail"].lower()


def test_farmer_cannot_order_own_produce(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(farmer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert resp.status_code == 403
    assert "not allowed" in resp.json()["detail"].lower()


def test_backend_calculates_total_amount(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=30.0,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    assert resp.status_code == 201

    body = resp.json()

    assert body["total_amount"] == "150.00"
    assert body["unit_price"] == "30.00"


def test_farmer_id_comes_from_produce(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    assert resp.status_code == 201

    body = resp.json()

    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    assert body["farmer_id"] == farmer_id


def test_produce_stock_decreases_after_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
        },
    )

    assert resp.status_code == 201

    resp = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["quantity"] == 80


def test_stock_cannot_become_negative(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=10,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert resp.status_code == 201

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 1,
        },
    )

    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Order review
# ---------------------------------------------------------------------------


def test_bulk_buyer_can_review(client: TestClient):
    """BULK_BUYER can use the shared order review endpoint."""
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="bulk@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="bulk@example.com",
    )

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
        },
    )

    assert resp.status_code == 200, resp.text

    body = resp.json()

    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 20
    assert body["unit_price"] == "25.00"
    assert body["total_amount"] == "500.00"
    assert body["available_stock"] == 100

    resp = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["quantity"] == 100


# ---------------------------------------------------------------------------
# View orders
# ---------------------------------------------------------------------------


def test_buyer_can_view_their_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    order_id = resp.json()["id"]

    resp = client.get(
        f"/api/orders/{order_id}",
        headers=auth_headers(buyer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_farmer_can_view_their_consumer_orders(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    resp = client.get(
        f"/api/orders/{order_id}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_unrelated_user_cannot_view_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    order_id = resp.json()["id"]

    register_user(
        client,
        email="other@example.com",
        role="CONSUMER",
    )
    other_token = obtain_token(
        client,
        email="other@example.com",
    )

    resp = client.get(
        f"/api/orders/{order_id}",
        headers=auth_headers(other_token),
    )

    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------


def test_buyer_can_cancel_pending_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "CANCELLED"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


def test_cancelling_restores_stock(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "CANCELLED"},
    )

    resp = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["quantity"] == 50


def test_cancelling_financed_order_voids_transaction_and_restores_credit(
    client: TestClient,
):
    """Cancelling a financed order voids its transaction and restores stock."""
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="cancel_financed_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="cancel_financed_buyer@example.com",
    )

    buyer_id = int(
        decode_access_token(buyer_token)["sub"]
    )

    db = SessionLocal()

    try:
        db.add(
            BuyerProfile(
                user_id=buyer_id,
                financing_preference="PLATFORM",
            )
        )

        relationship = FinancingRelationship(
            buyer_id=buyer_id,
            financier_id=buyer_id,
            credit_limit=1000,
            interest_rate=10,
            tenure_days=90,
            status="ACTIVE",
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        relationship_id = relationship.id

    finally:
        db.close()

    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
            "relationship_id": relationship_id,
        },
    )

    assert response.status_code == 201, response.text

    order = response.json()
    order_id = order["id"]

    db = SessionLocal()

    try:
        transaction = (
            db.query(FinancingTransaction)
            .filter(FinancingTransaction.order_id == order_id)
            .one()
        )

        assert transaction.status == "ACTIVE"
        assert transaction.principal == Decimal("500.00")

    finally:
        db.close()

    response = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "CANCELLED"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CANCELLED"

    response = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 100

    db = SessionLocal()

    try:
        transaction = db.get(
            FinancingTransaction,
            transaction.id,
        )

        assert transaction is not None
        assert transaction.status == "VOIDED"

        relationship = db.get(
            FinancingRelationship,
            relationship_id,
        )

        active_transactions = (
            db.query(FinancingTransaction)
            .filter(
                FinancingTransaction.relationship_id == relationship_id,
                FinancingTransaction.status == "ACTIVE",
            )
            .all()
        )

        outstanding_principal = sum(
            (
                transaction.principal
                for transaction in active_transactions
            ),
            Decimal("0.00"),
        )

        available_credit = (
            relationship.credit_limit - outstanding_principal
        )

        assert available_credit == Decimal("1000.00")

    finally:
        db.close()


def test_farmer_can_confirm_pending_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"


def test_farmer_can_complete_confirmed_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "COMPLETED"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"


def test_invalid_transition_rejected(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "PENDING"},
    )

    assert resp.status_code == 422
    assert "Invalid status transition" in resp.json()["detail"]


def test_completed_to_cancel_rejected(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    order_id = resp.json()["id"]

    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "COMPLETED"},
    )

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "CANCELLED"},
    )

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_get_order_404(client: TestClient):
    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.get(
        "/api/orders/99999",
        headers=auth_headers(buyer_token),
    )

    assert resp.status_code == 404


def test_list_orders_for_buyer(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    resp = client.get(
        "/api/orders",
        headers=auth_headers(buyer_token),
    )

    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_orders_for_farmer(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    resp = client.get(
        "/api/orders",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_can_view_orders(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(
        client,
        email="farmerA@example.com",
        quantity=50,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 5,
        },
    )

    register_user(
        client,
        email="admin@example.com",
        role="ADMIN",
    )
    admin_token = obtain_token(
        client,
        email="admin@example.com",
    )

    resp = client.get(
        "/api/orders",
        headers=auth_headers(admin_token),
    )

    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_orders_no_longer_accepted_role_query_param(client: TestClient):
    """The misleading '?role=...' query parameter was removed from GET /api/orders."""
    register_user(
        client,
        email="admin_only@example.com",
        role="ADMIN",
    )
    admin_token = obtain_token(
        client,
        email="admin_only@example.com",
    )

    resp = client.get(
        "/api/orders?role=CONSUMER",
        headers=auth_headers(admin_token),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_order_stock_atomic(client: TestClient):
    """Test that stock is never negative even with concurrent-like rejections."""
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=10,
    )

    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )
    buyer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert resp.status_code == 201

    resp = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200
    assert resp.json()["quantity"] == 0

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 1,
        },
    )

    assert resp.status_code == 409

    resp = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.json()["quantity"] == 0


# ---------------------------------------------------------------------------
# P3-P4 financing integration
# ---------------------------------------------------------------------------


def test_bulk_buyer_platform_financing_creates_transaction(
    client: TestClient,
):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="financed_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="financed_buyer@example.com",
    )

    register_user(
        client,
        email="financier_for_financed_order@example.com",
        role="FINANCIER",
    )

    buyer_id = int(
        decode_access_token(buyer_token)["sub"]
    )

    db = SessionLocal()

    try:
        profile = BuyerProfile(
            user_id=buyer_id,
            financing_preference="PLATFORM",
        )

        financier_id = int(
            decode_access_token(
                obtain_token(
                    client,
                    email="financier_for_financed_order@example.com",
                )
            )["sub"]
        )

        relationship = FinancingRelationship(
            buyer_id=buyer_id,
            financier_id=financier_id,
            credit_limit=1000,
            interest_rate=10,
            tenure_days=90,
            status="ACTIVE",
        )

        db.add(profile)
        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        relationship_id = relationship.id

    finally:
        db.close()

    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
            "relationship_id": relationship_id,
        },
    )

    assert response.status_code == 201, response.text

    order = response.json()

    assert order["quantity"] == 20
    assert order["total_amount"] == "500.00"

    db = SessionLocal()

    try:
        transactions = (
            db.query(FinancingTransaction)
            .filter(
                FinancingTransaction.relationship_id == relationship_id
            )
            .all()
        )

        assert len(transactions) == 1
        assert transactions[0].order_id == order["id"]
        assert transactions[0].principal == Decimal("500.00")
        assert transactions[0].status == "ACTIVE"

    finally:
        db.close()


def test_platform_financing_failure_rolls_back_order_and_stock(
    client: TestClient,
):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="limited_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="limited_buyer@example.com",
    )

    register_user(
        client,
        email="financier_for_limited_order@example.com",
        role="FINANCIER",
    )

    buyer_id = int(
        decode_access_token(buyer_token)["sub"]
    )

    db = SessionLocal()

    try:
        db.add(
            BuyerProfile(
                user_id=buyer_id,
                financing_preference="PLATFORM",
            )
        )

        financier_id = int(
            decode_access_token(
                obtain_token(
                    client,
                    email="financier_for_limited_order@example.com",
                )
            )["sub"]
        )

        relationship = FinancingRelationship(
            buyer_id=buyer_id,
            financier_id=financier_id,
            credit_limit=100,
            interest_rate=10,
            tenure_days=90,
            status="ACTIVE",
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        relationship_id = relationship.id

    finally:
        db.close()

    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 20,
            "relationship_id": relationship_id,
        },
    )

    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower()

    stock_response = client.get(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
    )

    assert stock_response.status_code == 200
    assert stock_response.json()["quantity"] == 100

    orders_response = client.get(
        "/api/orders",
        headers=auth_headers(buyer_token),
    )

    assert orders_response.status_code == 200
    assert orders_response.json() == []


def test_platform_financing_requires_active_relationship(
    client: TestClient,
):
    farmer_token, produce = register_farmer_with_produce(client)

    register_user(
        client,
        email="platform_without_relationship@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="platform_without_relationship@example.com",
    )

    buyer_id = int(
        decode_access_token(buyer_token)["sub"]
    )

    db = SessionLocal()

    try:
        db.add(
            BuyerProfile(
                user_id=buyer_id,
                financing_preference="PLATFORM",
            )
        )
        db.commit()

    finally:
        db.close()

    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert response.status_code == 400
    assert "relationship" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Direct financing transaction authorization
# ---------------------------------------------------------------------------


def test_direct_financing_transaction_requires_existing_order(
    client: TestClient,
):
    register_user(
        client,
        email="direct_finance_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="direct_finance_buyer@example.com",
    )

    buyer_id = int(
        decode_access_token(buyer_token)["sub"]
    )

    db = SessionLocal()

    try:
        relationship = FinancingRelationship(
            buyer_id=buyer_id,
            financier_id=buyer_id,
            credit_limit=1000,
            interest_rate=10,
            tenure_days=90,
            status="ACTIVE",
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        relationship_id = relationship.id

    finally:
        db.close()

    response = client.post(
        "/api/finance/transactions",
        headers=auth_headers(buyer_token),
        json={
            "relationship_id": relationship_id,
            "order_id": 99999,
            "principal": 500,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_direct_financing_transaction_cannot_use_another_buyers_order(
    client: TestClient,
):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    # Buyer A owns the order.
    register_user(
        client,
        email="order_owner@example.com",
        role="BULK_BUYER",
    )
    owner_token = obtain_token(
        client,
        email="order_owner@example.com",
    )

    order_response = client.post(
        "/api/orders",
        headers=auth_headers(owner_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert order_response.status_code == 201, order_response.text

    order = order_response.json()

    # Buyer B owns the financing relationship.
    register_user(
        client,
        email="financing_attacker@example.com",
        role="BULK_BUYER",
    )
    attacker_token = obtain_token(
        client,
        email="financing_attacker@example.com",
    )

    attacker_id = int(
        decode_access_token(attacker_token)["sub"]
    )

    db = SessionLocal()

    try:
        relationship = FinancingRelationship(
            buyer_id=attacker_id,
            financier_id=attacker_id,
            credit_limit=1000,
            interest_rate=10,
            tenure_days=90,
            status="ACTIVE",
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        relationship_id = relationship.id

    finally:
        db.close()

    response = client.post(
        "/api/finance/transactions",
        headers=auth_headers(attacker_token),
        json={
            "relationship_id": relationship_id,
            "order_id": order["id"],
            "principal": 250,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You are not authorized to finance this order"
    )


def test_direct_financing_transaction_cannot_be_created_twice(
    client: TestClient,
):
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    register_user(
        client,
        email="duplicate_finance_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="duplicate_finance_buyer@example.com",
    )

    buyer_id = int(
        decode_access_token(buyer_token)["sub"]
    )

    order_response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert order_response.status_code == 201, order_response.text

    order = order_response.json()

    db = SessionLocal()

    try:
        relationship = FinancingRelationship(
            buyer_id=buyer_id,
            financier_id=buyer_id,
            credit_limit=1000,
            interest_rate=10,
            tenure_days=90,
            status="ACTIVE",
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        relationship_id = relationship.id

    finally:
        db.close()

    transaction_payload = {
        "relationship_id": relationship_id,
        "order_id": order["id"],
        "principal": 250,
    }

    response = client.post(
        "/api/finance/transactions",
        headers=auth_headers(buyer_token),
        json=transaction_payload,
    )

    assert response.status_code == 201, response.text

    response = client.post(
        "/api/finance/transactions",
        headers=auth_headers(buyer_token),
        json=transaction_payload,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "This order already has a financing transaction"
    )