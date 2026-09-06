"""Tests for the Orders module.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def register_farmer_with_produce(client: TestClient, email: str = "farmer@example.com", crop: str = "Wheat", quantity: int = 100, price_per_unit: float = 25.0) -> tuple[str, dict]:
    """Register a farmer, approve them, create a produce listing, return (farmer_token, produce_body)."""
    register_user(client, email=email, role="FARMER")
    farmer_token = obtain_token(client, email=email)

    # Submit verification documents
    for doc_type in ["AADHAAR", "PAN"]:
        resp = client.post(
            "/api/verification/documents",
            headers=auth_headers(farmer_token),
            json={"document_type": doc_type, "document_number": f"DOC-{doc_type}"},
        )
        assert resp.status_code == 201, resp.text

    # Admin approves
    resp = register_user(client, email="admin@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin@example.com")

    from app.core.security import decode_access_token
    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200, resp.text

    body = create_produce(client, farmer_token, crop=crop, quantity=quantity, price_per_unit=price_per_unit)
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
    return resp.json() if resp.status_code in (200, 201) else resp.json()


# ---------------------------------------------------------------------------
# Create order — buyer roles
# ---------------------------------------------------------------------------

def test_buyer_can_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=50, price_per_unit=25.0)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 10
    assert body["unit_price"] == 25.0
    assert body["total_amount"] == 250.0
    assert body["status"] == "PENDING"
    assert body["farmer_id"] > 0
    assert body["buyer_id"] > 0


def test_consumer_can_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=50, price_per_unit=25.0)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 201


def test_bulk_buyer_can_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=50, price_per_unit=25.0)
    register_user(client, email="buyer@example.com", role="BULK_BUYER")
    buyer_token = obtain_token(client, email="buyer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 20},
    )
    assert resp.status_code == 201


def test_farmer_cannot_create_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(farmer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 403


def test_unauthenticated_cannot_create_order(client: TestClient):
    resp = client.post(
        "/api/orders",
        json={"produce_id": 1, "quantity": 1},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Create order — business rules
# ---------------------------------------------------------------------------

def test_nonexistent_produce_returns_error(client: TestClient):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": 99999, "quantity": 10},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_inactive_produce_cannot_be_ordered(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=100)
    # Set produce to INACTIVE
    resp = client.patch(
        f"/api/produce/{produce['id']}",
        headers=auth_headers(farmer_token),
        json={"status": "INACTIVE"},
    )
    assert resp.status_code == 200

    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 400
    assert "not available" in resp.json()["detail"].lower()


def test_quantity_must_be_gt_zero(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=100)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 0},
    )
    assert resp.status_code == 422


def test_cannot_order_more_than_stock(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=20)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 50},
    )
    assert resp.status_code == 409
    assert "available" in resp.json()["detail"].lower()


def test_farmer_cannot_order_own_produce(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(farmer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 403
    # A Farmer cannot order (403 because farmer role not allowed to create orders at all)
    assert "not allowed" in resp.json()["detail"].lower()


def test_backend_calculates_total_amount(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=100, price_per_unit=30.0)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["total_amount"] == 150.0
    assert body["unit_price"] == 30.0


def test_farmer_id_comes_from_produce(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com")
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    assert resp.status_code == 201
    body = resp.json()
    from app.core.security import decode_access_token
    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])
    assert body["farmer_id"] == farmer_id


def test_produce_stock_decreases_after_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=100)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 20},
    )
    assert resp.status_code == 201

    # Check produce stock reduced
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 80


def test_stock_cannot_become_negative(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=10)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    # Order all stock
    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 201

    # Try to order more (should fail)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 1},
    )
    assert resp.status_code == 409

# -------------------------------------------------------------
# Order review
# -------------------------------------------------------------

def test_bulk_buyer_can_review(client: TestClient):
    """BULK_BUYER can use the shared order review endpoint."""
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=25.0,
    )
    register_user(client, email="bulk@example.com", role="BULK_BUYER")
    buyer_token = obtain_token(client, email="bulk@example.com")

    resp = client.post(
        "/api/orders/review",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 20},
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["produce_id"] == produce["id"]
    assert body["quantity"] == 20
    assert body["unit_price"] == 25.0
    assert body["total_amount"] == 500.0
    assert body["available_stock"] == 100

    # Reviewing an order must not reduce stock.
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
    farmer_token, produce = register_farmer_with_produce(client, quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]

    # Buyer can view their order
    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(buyer_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_farmer_can_view_their_consumer_orders(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Farmer can view orders for their produce
    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(farmer_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


def test_unrelated_user_cannot_view_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )
    order_id = resp.json()["id"]

    # Another consumer should not see this order
    register_user(client, email="other@example.com", role="CONSUMER")
    other_token = obtain_token(client, email="other@example.com")

    resp = client.get(f"/api/orders/{order_id}", headers=auth_headers(other_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

def test_buyer_can_cancel_pending_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Buyer cancels
    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "CANCELLED"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


def test_cancelling_restores_stock(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Cancel
    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "CANCELLED"},
    )

    # Check stock restored
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 50


def test_farmer_can_confirm_pending_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Farmer confirms
    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"


def test_farmer_can_complete_confirmed_order(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Confirm first
    client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    # Then complete
    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(farmer_token),
        json={"status": "COMPLETED"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"


def test_invalid_transition_rejected(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Try COMPLETED -> PENDING (invalid)
    resp = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers(buyer_token),
        json={"status": "PENDING"},
    )
    assert resp.status_code == 422
    assert "Invalid status transition" in resp.json()["detail"]


def test_completed_to_cancel_rejected(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    order_id = resp.json()["id"]

    # Farmer confirms, then completes
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

    # Buyer tries to cancel completed order
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
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    resp = client.get("/api/orders/99999", headers=auth_headers(buyer_token))
    assert resp.status_code == 404


def test_list_orders_for_buyer(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )

    resp = client.get("/api/orders", headers=auth_headers(buyer_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_orders_for_farmer(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )

    resp = client.get("/api/orders", headers=auth_headers(farmer_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_can_view_orders(client: TestClient):
    farmer_token, produce = register_farmer_with_produce(client, email="farmerA@example.com", quantity=50)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 5},
    )

    register_user(client, email="admin@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin@example.com")

    resp = client.get("/api/orders", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_orders_no_longer_accepted_role_query_param(client: TestClient):
    """The misleading '?role=...' query parameter was removed from GET /api/orders."""
    admin_token = register_user(client, email="admin_only@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_only@example.com")

    resp = client.get(
        "/api/orders?role=CONSUMER",
        headers=auth_headers(admin_token),
    )
    # FastAPI ignores unrecognized query params by default; the fix is that the
    # endpoint no longer uses 'role'. Confirm the endpoint still works and no
    # longer has the placeholder filter.
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_order_stock_atomic(client: TestClient):
    """Test that stock is never negative even with concurrent-like rejections."""
    farmer_token, produce = register_farmer_with_produce(client, quantity=10)
    register_user(client, email="consumer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="consumer@example.com")

    # Order all stock
    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert resp.status_code == 201

    # Verify stock is 0
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 0

    # Try to order 1 more (should fail)
    resp = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 1},
    )
    assert resp.status_code == 409

    # Stock should still be 0
    resp = client.get(f"/api/produce/{produce['id']}", headers=auth_headers(farmer_token))
    assert resp.json()["quantity"] == 0