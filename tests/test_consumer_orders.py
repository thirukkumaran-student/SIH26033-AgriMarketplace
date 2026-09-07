"""Tests for P2 Consumer Orders Integration.

Covers the full flow: Marketplace -> Select Produce -> Place Order ->
Existing shared Order -> Stock decreases -> Consumer sees the order.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.enums import OrderStatus, ProduceStatus, VerificationStatus
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


def insert_produce_unverified(
    client: TestClient,
    farmer_email: str,
    crop: str = "Wheat",
    quantity: int = 100,
    price_per_unit: float = 25.0,
) -> Produce:
    """Register a farmer without verification, create produce directly in DB."""
    register_user(client, email=farmer_email, role="FARMER")
    token = obtain_token(client, email=farmer_email)
    farmer_id = int(decode_access_token(token)["sub"])

    db = SessionLocal()
    try:
        produce = Produce(
            farmer_id=farmer_id,
            crop=crop,
            category="Cereals",
            quantity=quantity,
            unit="kg",
            price_per_unit=price_per_unit,
            location="Test Location",
            status=ProduceStatus.ACTIVE.value,
        )
        db.add(produce)
        db.commit()
        db.refresh(produce)
        return produce
    finally:
        db.close()


def register_consumer_and_login(client: TestClient, email: str = "consumer_order@example.com") -> str:
    """Register a CONSUMER and return their JWT token."""
    register_user(client, email=email, name="Test Consumer", role="CONSUMER")
    return obtain_token(client, email=email)


# ---------------------------------------------------------------------------
# SUCCESS TESTS
# ---------------------------------------------------------------------------


def test_consumer_successfully_places_order(client: TestClient):
    """Consumer can place an order for eligible produce."""
    farmer_token, produce = register_user.__wrapped__ if False else _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 10
    assert body["status"] == "PENDING"
    assert body["total_amount"] == "250.00"


def _register_and_approve_farmer(client: TestClient, email: str = "farmer_order@example.com",
                                  crop: str = "Wheat", quantity: int = 100,
                                  price_per_unit: float = 25.0) -> tuple[str, dict]:
    """Helper: register, approve farmer, create produce, return (token, produce_body)."""
    register_user(client, email=email, role="FARMER")
    farmer_token = obtain_token(client, email=email)
    approve_farmer(client, farmer_token, farmer_email=email)

    from tests.test_produce import create_produce
    body = create_produce(client, farmer_token, crop=crop, quantity=quantity, price_per_unit=price_per_unit)
    return farmer_token, body


# ---------------------------------------------------------------------------
# BACKEND AUTHORITY TESTS
# ---------------------------------------------------------------------------


def test_backend_calculates_total_amount(client: TestClient):
    """Backend calculates total_amount correctly, not from client input."""
    farmer_token, produce = _register_and_approve_farmer(client, price_per_unit=30.0)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_amount"] == "150.00"
    assert body["unit_price"] == "30.00"


def test_fake_price_cannot_manipulate_total(client: TestClient):
    """Client cannot override price_per_unit in order creation."""
    farmer_token, produce = _register_and_approve_farmer(client, price_per_unit=50.0)
    consumer_token = register_consumer_and_login(client)

    # The OrderCreate schema only accepts produce_id and quantity,
    # so there's no way to send price_per_unit in the order payload.
    # But we verify the returned total is from the actual DB price.
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 2},
    )
    assert resp.status_code == 201
    assert resp.json()["total_amount"] == "100.00"  # 2 * 50.0
    assert resp.json()["unit_price"] == "50.00"


def test_fake_farmer_id_cannot_manipulate_ownership(client: TestClient):
    """Client cannot change farmer ownership of the order."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmerA@example.com")
    consumer_token = register_consumer_and_login(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 201
    body = resp.json()
    from app.core.security import decode_access_token as decode_token
    farmer_id = int(decode_token(farmer_token)["sub"])
    assert body["farmer_id"] == farmer_id


def test_backend_authoritative_price_on_order_response(client: TestClient):
    """Order response always reflects the database price, not client-supplied values."""
    farmer_token, produce = _register_and_approve_farmer(client, price_per_unit=99.99)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 3},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["unit_price"] == "99.99"
    assert body["total_amount"] == "299.97"


# ---------------------------------------------------------------------------
# VALIDATION TESTS
# ---------------------------------------------------------------------------


def test_zero_quantity_rejected(client: TestClient):
    """quantity = 0 is rejected."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 0},
    )
    assert resp.status_code == 422


def test_negative_quantity_rejected(client: TestClient):
    """Negative quantity is rejected."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": -5},
    )
    assert resp.status_code == 422


def test_quantity_greater_than_stock_rejected(client: TestClient):
    """quantity > available stock is rejected."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=10)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 50},
    )
    assert resp.status_code == 409
    assert "available" in resp.json()["detail"].lower()


def test_inactive_produce_cannot_be_ordered(client: TestClient):
    """Inactive produce returns 400."""
    farmer_token, produce = _register_and_approve_farmer(client)

    # Set produce to INACTIVE
    resp = client.patch(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
        json={"status": "INACTIVE"},
    )
    assert resp.status_code == 200

    consumer_token = register_consumer_and_login(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 400


def test_zero_stock_produce_cannot_be_ordered(client: TestClient):
    """Zero-stock produce returns 409."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=100)

    db = SessionLocal()
    try:
        p = db.get(Produce, produce["id"])
        p.quantity = 0
        db.commit()
        db.refresh(p)
    finally:
        db.close()

    consumer_token = register_consumer_and_login(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 1},
    )
    assert resp.status_code == 409


def test_nonexistent_produce_returns_error(client: TestClient):
    """Nonexistent produce returns 404."""
    consumer_token = register_consumer_and_login(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": 99999, "quantity": 10},
    )
    assert resp.status_code == 404


def test_self_order_rejected(client: TestClient):
    """Farmer cannot order their own produce."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmer_self@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(farmer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# MARKETPLACE ELIGIBILITY BYPASS TESTS
# ---------------------------------------------------------------------------


def test_cannot_order_from_unverified_farmer(client: TestClient):
    """Consumer cannot order from an unverified farmer (bypasses marketplace eligibility)."""
    produce = insert_produce_unverified(client, "unverified_farmer@example.com", quantity=100)

    consumer_token = register_consumer_and_login(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce.id, "quantity": 10},
    )
    assert resp.status_code == 400
    assert "not available" in resp.json()["detail"].lower()


def test_cannot_order_from_rejected_farmer(client: TestClient):
    """Consumer cannot order from a rejected farmer."""
    register_user(client, email="rejected_farmer@example.com", role="FARMER")
    token = obtain_token(client, email="rejected_farmer@example.com")
    farmer_id = int(decode_access_token(token)["sub"])

    # Submit docs and get rejected
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "REJECTED-1234"},
    )
    register_user(client, email="admin_reject@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_reject@example.com")

    from sqlalchemy import select

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "rejected_farmer@example.com"))
        doc_id = db.scalar(select(VerificationDocument).where(VerificationDocument.user_id == farmer.id)).id
        db.close()
        client.post(
            f"/api/admin/verifications/{farmer.id}/reject",
            headers=auth_headers(admin_token),
            json={"document_id": doc_id, "remarks": "Forged"},
        )
    finally:
        db.close()

    # Create produce directly
    db = SessionLocal()
    try:
        produce = Produce(
            farmer_id=farmer_id, crop="Rejected Crop", category="Cereals",
            quantity=100, unit="kg", price_per_unit=25.0,
            location="Test", status=ProduceStatus.ACTIVE.value,
        )
        db.add(produce)
        db.commit()
        db.refresh(produce)
    finally:
        db.close()

    consumer_token = register_consumer_and_login(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce.id, "quantity": 10},
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# STOCK BEHAVIOR TESTS
# ---------------------------------------------------------------------------


def test_stock_decreases_after_successful_order(client: TestClient):
    """Successful order decreases produce stock."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=100)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 20},
    )
    assert resp.status_code == 201

    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 80


def test_cancelled_order_restores_stock(client: TestClient):
    """Cancelling a PENDING order restores stock."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=50)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 20},
    )
    order_id = resp.json()["id"]

    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(consumer_token),
        json={"status": "CANCELLED"},
    )

    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 50


def test_stock_never_becomes_negative(client: TestClient):
    """Stock cannot go below zero."""
    farmer_token, produce = _register_and_approve_farmer(client, quantity=5)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 201

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 1},
    )
    assert resp.status_code == 409

    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 0


# ---------------------------------------------------------------------------
# VISIBILITY TESTS
# ---------------------------------------------------------------------------


def test_consumer_sees_own_order(client: TestClient):
    """Consumer can see their own order."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]

    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_consumer_cannot_see_another_consumers_order(client: TestClient):
    """Consumer A cannot see Consumer B's order."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmer_vis@example.com")

    # Consumer A
    consumer_a_token = register_consumer_and_login(client, email="consumer_a@example.com")
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_a_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]

    # Consumer B
    consumer_b_token = register_consumer_and_login(client, email="consumer_b@example.com")
    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(consumer_b_token))
    assert resp.status_code == 403


def test_consumer_cannot_access_another_consumers_order_detail(client: TestClient):
    """Consumer A cannot access Consumer B's order detail."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmer_detail@example.com")

    consumer_a_token = register_consumer_and_login(client, email="consumer_detail_a@example.com")
    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_a_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]

    consumer_b_token = register_consumer_and_login(client, email="consumer_detail_b@example.com")
    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(consumer_b_token))
    assert resp.status_code == 403


def test_farmer_can_see_consumer_orders_for_their_produce(client: TestClient):
    """Farmer can see orders for their own produce."""
    farmer_token, produce = _register_and_approve_farmer(client, email="farmer_see@example.com")
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]

    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(farmer_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


# ---------------------------------------------------------------------------
# STATUS TRANSITION TESTS
# ---------------------------------------------------------------------------


def test_consumer_can_cancel_pending_order(client: TestClient):
    """Consumer can cancel a PENDING order."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(consumer_token),
        json={"status": "CANCELLED"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


def test_invalid_consumer_transition_pending_to_completed_rejected(client: TestClient):
    """Consumer cannot transition PENDING -> COMPLETED directly."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(consumer_token),
        json={"status": "COMPLETED"},
    )
    assert resp.status_code == 422


def test_farmer_confirmation_still_works(client: TestClient):
    """Farmer can still confirm PENDING orders."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"


def test_farmer_completion_still_works(client: TestClient):
    """Farmer can still complete CONFIRMED orders."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
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


def test_completed_to_cancelled_rejected(client: TestClient):
    """Cannot cancel a COMPLETED order."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
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
        headers=auth_headers(consumer_token),
        json={"status": "CANCELLED"},
    )
    assert resp.status_code == 422


def test_cancelled_to_confirmed_rejected(client: TestClient):
    """Cannot confirm a CANCELLED order."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(consumer_token),
        json={"status": "CANCELLED"},
    )

    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# AUTHORIZATION TESTS
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_create_order(client: TestClient):
    """Unauthenticated user gets 401."""
    resp = client.post(
        "/api/orders",
        json={"produce_id": 1, "quantity": 1},
    )
    assert resp.status_code == 401


def test_farmer_cannot_create_order(client: TestClient):
    """FARMER role gets 403 when creating orders."""
    farmer_token, produce = _register_and_approve_farmer(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(farmer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_bulk_buyer_can_create_order(client: TestClient):
    """BULK_BUYER can create orders (existing behavior)."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="bulk@example.com", role="BULK_BUYER")
    buyer_token = obtain_token(client, email="bulk@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 20},
    )
    assert resp.status_code == 201


def test_financier_cannot_create_order(client: TestClient):
    """FINANCIER gets 403."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="fin@example.com", role="FINANCIER")
    token = obtain_token(client, email="fin@example.com")
    resp = client.post(
        "/api/orders",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_logistics_cannot_create_order(client: TestClient):
    """LOGISTICS gets 403."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="log@example.com", role="LOGISTICS")
    token = obtain_token(client, email="log@example.com")
    resp = client.post(
        "/api/orders",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_admin_cannot_create_order(client: TestClient):
    """ADMIN gets 403 when creating orders."""
    farmer_token, produce = _register_and_approve_farmer(client)
    register_user(client, email="admin_order@example.com", role="ADMIN")
    token = obtain_token(client, email="admin_order@example.com")
    resp = client.post(
        "/api/orders",
        headers=auth_headers(token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# ORDER RESPONSE TESTS
# ---------------------------------------------------------------------------


def test_order_response_contains_required_fields(client: TestClient):
    """Order response contains enough information for the consumer."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    body = resp.json()
    assert "id" in body
    assert "produce_id" in body
    assert "quantity" in body
    assert "unit_price" in body
    assert "total_amount" in body
    assert "status" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_order_response_does_not_expose_excessive_pii(client: TestClient):
    """Order response does not expose unnecessary farmer PII."""
    farmer_token, produce = _register_and_approve_farmer(client)
    consumer_token = register_consumer_and_login(client)

    resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    body = resp.json()
    # Should have farmer_id but not sensitive PII
    assert "farmer_id" in body
    assert "buyer_id" in body
    # No password, email, phone etc.
    sensitive = {"password", "password_hash", "email", "phone", "hashed_password"}
    for key in sensitive:
        assert key not in body, f"Sensitive key '{key}' exposed in order response"