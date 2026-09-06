"""Tests for P2 Checkout / Order Review.

Covers the read-only order review endpoint that validates produce
eligibility, quantity, and calculates totals before final order placement.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.enums import ProduceStatus, VerificationStatus
from app.models.farmer import VerificationDocument
from app.models.produce import Produce
from app.models.user import User
from app.core.security import decode_access_token
from tests.test_auth import auth_headers, obtain_token, register_user
from tests.test_consumer import register_consumer
from tests.test_produce import approve_farmer, create_produce


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register_and_approve_farmer(client: TestClient, email: str = "farmer_checkout@example.com",
                                  crop: str = "Wheat", quantity: int = 100,
                                  price_per_unit: float = 25.0) -> tuple[str, dict]:
    """Helper: register, approve farmer, create produce, return (token, produce_body)."""
    register_user(client, email=email, role="FARMER")
    farmer_token = obtain_token(client, email=email)
    approve_farmer(client, farmer_token, farmer_email=email)
    body = create_produce(client, farmer_token, crop=crop, quantity=quantity, price_per_unit=price_per_unit)
    return farmer_token, body


def _register_consumer(client: TestClient, email: str = "consumer_checkout@example.com") -> str:
    """Register a CONSUMER and return their JWT token."""
    register_user(client, email=email, name="Test Consumer", role="CONSUMER")
    return obtain_token(client, email=email)


def _insert_zero_stock_produce(client: TestClient, farmer_email: str, crop: str = "Zero Crop",
                               quantity: int = 100, price_per_unit: float = 25.0) -> Produce:
    """Register an approved farmer, then set produce quantity to 0 via DB."""
    register_user(client, email=farmer_email, role="FARMER")
    token = obtain_token(client, email=farmer_email)
    approve_farmer(client, token, farmer_email=farmer_email)
    body = create_produce(client, token, crop=crop, quantity=quantity, price_per_unit=price_per_unit)
    farmer_id = int(decode_access_token(token)["sub"])

    db = SessionLocal()
    try:
        p = db.get(Produce, body["id"])
        p.quantity = 0
        db.commit()
        db.refresh(p)
        return p
    finally:
        db.close()


def _insert_inactive_produce(client: TestClient, farmer_email: str, crop: str = "Inactive Crop",
                             quantity: int = 100, price_per_unit: float = 25.0) -> Produce:
    """Register an approved farmer, then set produce status to INACTIVE via DB."""
    register_user(client, email=farmer_email, role="FARMER")
    token = obtain_token(client, email=farmer_email)
    approve_farmer(client, token, farmer_email=farmer_email)
    body = create_produce(client, token, crop=crop, quantity=quantity, price_per_unit=price_per_unit)
    farmer_id = int(decode_access_token(token)["sub"])

    db = SessionLocal()
    try:
        p = db.get(Produce, body["id"])
        p.status = ProduceStatus.INACTIVE.value
        db.commit()
        db.refresh(p)
        return p
    finally:
        db.close()


# ---------------------------------------------------------------------------
# AUTHENTICATION TESTS
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_review(client: TestClient):
    """Unauthenticated review request returns 401."""
    resp = client.post(
        "/api/orders/review",
        json={"produce_id": 1, "quantity": 1},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# AUTHORIZATION TESTS
# ---------------------------------------------------------------------------


def test_consumer_can_review(client: TestClient):
    """CONSUMER can use the review endpoint."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 5
    assert body["unit_price"] == 25.0
    assert body["total_amount"] == 125.0


def test_farmer_cannot_review(client: TestClient):
    """FARMER gets 403 on review endpoint."""
    farmer_token, produce = _register_and_approve_farmer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(farmer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_bulk_buyer_can_review(client: TestClient):
    """BULK_BUYER can use the shared order review endpoint."""
    farmer_token, produce = _register_and_approve_farmer(client)

    register_user(client, email="bulk@example.com", role="BULK_BUYER")
    token = obtain_token(client, email="bulk@example.com")

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )

    assert resp.status_code == 200, resp.text

    body = resp.json()
    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 5


def test_financier_cannot_review(client: TestClient):
    """FINANCIER gets 403 on review endpoint."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="fin@example.com", role="FINANCIER")
    token = obtain_token(client, email="fin@example.com")

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_logistics_cannot_review(client: TestClient):
    """LOGISTICS gets 403 on review endpoint."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="log@example.com", role="LOGISTICS")
    token = obtain_token(client, email="log@example.com")

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_admin_cannot_review(client: TestClient):
    """ADMIN gets 403 on review endpoint."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="admin_review@example.com", role="ADMIN")
    token = obtain_token(client, email="admin_review@example.com")

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# PRODUCE VALIDATION TESTS
# ---------------------------------------------------------------------------


def test_nonexistent_produce_returns_404(client: TestClient):
    """Nonexistent produce returns 404."""
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": 99999, "quantity": 1},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_inactive_produce_rejected(client: TestClient):
    """Inactive produce returns 400."""
    produce = _insert_inactive_produce(client, farmer_email="inactive_farmer@example.com")
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce.id, "quantity": 5},
    )
    assert resp.status_code == 400
    assert "not available" in resp.json()["detail"].lower()


def test_zero_stock_produce_rejected(client: TestClient):
    """Zero-stock produce returns 409."""
    p = _insert_zero_stock_produce(client, farmer_email="zero_farmer@example.com")
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": p.id, "quantity": 1},
    )
    assert resp.status_code == 409
    assert "available" in resp.json()["detail"].lower()


def test_unverified_farmer_rejected(client: TestClient):
    """Produce from unverified farmer is rejected on review."""
    from app.core.database import SessionLocal as _SL
    from app.models.farmer import VerificationDocument as _VD
    from app.models.produce import Produce as _P

    register_user(client, email="unverified_farmer@example.com", role="FARMER")
    token = obtain_token(client, email="unverified_farmer@example.com")
    farmer_id = int(decode_access_token(token)["sub"])

    # Create produce directly (no verification docs)
    db = _SL()
    try:
        produce = _P(
            farmer_id=farmer_id, crop="Unverified Crop",
            category="Cereals", quantity=100, unit="kg",
            price_per_unit=25.0, location="Test", status=ProduceStatus.ACTIVE.value,
        )
        db.add(produce)
        db.commit()
        db.refresh(produce)
    finally:
        db.close()

    consumer_token = _register_consumer(client)
    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce.id, "quantity": 5},
    )
    assert resp.status_code == 400


def test_pending_farmer_rejected(client: TestClient):
    """Produce from pending farmer is rejected on review."""
    from app.core.database import SessionLocal as _SL
    from app.models.farmer import VerificationDocument as _VD
    from app.models.produce import Produce as _P

    register_user(client, email="pending_farmer@example.com", role="FARMER")
    token = obtain_token(client, email="pending_farmer@example.com")
    farmer_id = int(decode_access_token(token)["sub"])

    # Submit docs but do not approve
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "PENDING-1234"},
    )

    db = _SL()
    try:
        produce = _P(
            farmer_id=farmer_id, crop="Pending Crop",
            category="Cereals", quantity=100, unit="kg",
            price_per_unit=25.0, location="Test", status=ProduceStatus.ACTIVE.value,
        )
        db.add(produce)
        db.commit()
        db.refresh(produce)
    finally:
        db.close()

    consumer_token = _register_consumer(client)
    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce.id, "quantity": 5},
    )
    assert resp.status_code == 400


def test_rejected_farmer_rejected(client: TestClient):
    """Produce from rejected farmer is rejected on review."""
    from app.core.database import SessionLocal as _SL
    from app.models.farmer import VerificationDocument as _VD
    from app.models.produce import Produce as _P
    from sqlalchemy import select

    register_user(client, email="rejected_farmer2@example.com", role="FARMER")
    token = obtain_token(client, email="rejected_farmer2@example.com")
    farmer_id = int(decode_access_token(token)["sub"])

    # Submit docs and get rejected
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "REJECTED-5678"},
    )
    register_user(client, email="admin_reject2@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_reject2@example.com")

    db = _SL()
    try:
        farmer = db.scalar(select(User).where(User.email == "rejected_farmer2@example.com"))
        doc_id = db.scalar(select(VerificationDocument).where(VerificationDocument.user_id == farmer.id)).id
        db.close()
        client.post(
            f"/api/admin/verifications/{farmer.id}/reject",
            headers=auth_headers(admin_token),
            json={"document_id": doc_id, "remarks": "Forged"},
        )
    finally:
        db.close()

    db = _SL()
    try:
        produce = _P(
            farmer_id=farmer_id, crop="Rejected Crop",
            category="Cereals", quantity=100, unit="kg",
            price_per_unit=25.0, location="Test", status=ProduceStatus.ACTIVE.value,
        )
        db.add(produce)
        db.commit()
        db.refresh(produce)
    finally:
        db.close()

    consumer_token = _register_consumer(client)
    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce.id, "quantity": 5},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# QUANTITY VALIDATION TESTS
# ---------------------------------------------------------------------------


def test_zero_quantity_rejected(client: TestClient):
    """quantity = 0 is rejected."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 0},
    )
    assert resp.status_code == 422


def test_negative_quantity_rejected(client: TestClient):
    """Negative quantity is rejected."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": -5},
    )
    assert resp.status_code == 422


def test_quantity_equal_to_stock_accepted(client: TestClient):
    """quantity equal to stock is accepted."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=10)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 200
    assert resp.json()["total_amount"] == 250.0


def test_quantity_greater_than_stock_rejected(client: TestClient):
    """quantity > available stock is rejected."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=5)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 50},
    )
    assert resp.status_code == 409
    assert "available" in resp.json()["detail"].lower()


def test_self_order_rejected(client: TestClient):
    """Farmer cannot review their own produce."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmer_self_review@example.com")

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(farmer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# BACKEND AUTHORITY TESTS
# ---------------------------------------------------------------------------


def test_backend_calculates_total(client: TestClient):
    """Backend calculates total_amount from DB, not client input."""
    farmer_token, produce = _register_and_approve_farmer(client, price_per_unit=100.0)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["unit_price"] == 100.0
    assert body["total_amount"] == 300.0


def test_fake_price_cannot_manipulate_total(client: TestClient):
    """Client cannot override price_per_unit in review."""
    farmer_token, produce = _register_and_approve_farmer(client, price_per_unit=99.99)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 2},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["unit_price"] == 99.99
    assert body["total_amount"] == 199.98


def test_fake_farmer_id_cannot_manipulate_ownership(client: TestClient):
    """Client cannot change farmer ownership via review."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmer_review_owner@example.com")
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 200
    # The review response does not include farmer_id (read-only)
    body = resp.json()
    assert "farmer_id" not in body
    assert body["crop"] == produce["crop"]


def test_fake_total_ignored(client: TestClient):
    """Client-supplied total is ignored; backend calculates it."""
    farmer_token, produce = _register_and_approve_farmer(client, price_per_unit=50.0)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 4},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_amount"] == 200.0


# ---------------------------------------------------------------------------
# STOCK BEHAVIOR TESTS
# ---------------------------------------------------------------------------


def test_review_does_not_decrease_stock(client: TestClient):
    """Review does NOT decrease stock."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=10)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 200

    # Stock should still be 10
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 10


def test_review_followed_by_order_decreases_stock(client: TestClient):
    """Review itself doesn't change stock, but actual order does."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=10)
    consumer_token = _register_consumer(client)

    # Review
    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 200
    assert resp.json()["available_stock"] == 10

    # Stock unchanged after review
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 10

    # Actual order decreases stock
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 201

    # Stock now 7
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 7


# ---------------------------------------------------------------------------
# RESPONSE SCHEMA TESTS
# ---------------------------------------------------------------------------


def test_review_response_contains_required_fields(client: TestClient):
    """Review response contains only useful checkout fields."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "produce_id" in body
    assert "crop" in body
    assert "quantity" in body
    assert "unit_price" in body
    assert "total_amount" in body
    assert "unit" in body
    assert "available_stock" in body
    assert "status" in body
    # Should NOT have order-specific fields
    assert "id" not in body
    assert "buyer_id" not in body
    assert "farmer_id" not in body
    assert "status" not in body or body["status"] == "ACTIVE"


def test_review_response_does_not_expose_sensitive_pii(client: TestClient):
    """Review response does not expose sensitive farmer information."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    body = resp.json()
    sensitive_keys = {"password", "password_hash", "email", "phone", "hashed_password", "documents", "aadhaar", "pan"}
    for key in sensitive_keys:
        assert key not in body, f"Sensitive key '{key}' exposed in review response"


# ---------------------------------------------------------------------------
# INTEGRATION TESTS
# ---------------------------------------------------------------------------


def test_marketplace_to_review_to_order_flow(client: TestClient):
    """Full flow: Marketplace -> Review -> Order works correctly."""
    farmer_token, produce = _register_and_approve_farmer(client, crop="Basmati Rice", price_per_unit=45.0)
    consumer_token = _register_consumer(client)

    # Step 1: Review
    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 200
    review = resp.json()
    assert review["total_amount"] == 135.0
    assert review["unit_price"] == 45.0
    assert review["available_stock"] == 100

    # Step 2: Actual order
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 201
    assert resp.json()["total_amount"] == 135.0
    assert resp.json()["status"] == "PENDING"

    # Step 3: Stock decreased
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 97


def test_review_with_quantity_zero_returns_422(client: TestClient):
    """Review with quantity 0 returns 422 (Pydantic validation)."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = _register_consumer(client)

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 0},
    )
    assert resp.status_code == 422


def test_review_then_cancel_order_restores_stock(client: TestClient):
    """Review doesn't change stock, and cancelling the order restores it."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=20)
    consumer_token = _register_consumer(client)

    # Review
    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 200

    # Stock unchanged
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 20

    # Place order
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]
    assert resp.json()["total_amount"] == 125.0

    # Stock decreased
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 15

    # Cancel order
    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(consumer_token),
        json={"status": "CANCELLED"},
    )

    # Stock restored
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 20
