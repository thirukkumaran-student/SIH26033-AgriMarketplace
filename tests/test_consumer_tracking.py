"""Tests for P2 Consumer Tracking / Shipment Module.

Covers the consumer-facing shipment tracking endpoint that reads
existing shipment data via the Order → Shipment relationship.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user
from tests.test_shipment import register_farmer_with_order, create_shipment


# ---------------------------------------------------------------------------
# AUTHENTICATION TESTS
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_see_shipments(client: TestClient):
    """Unauthenticated request returns 401."""
    resp = client.get("/api/consumer/shipments")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# AUTHORIZATION TESTS
# ---------------------------------------------------------------------------


def test_consumer_can_see_shipments(client: TestClient):
    """CONSUMER can access /api/consumer/shipments."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 1
    assert body[0]["id"] == shipment["id"]


def test_farmer_cannot_access_consumer_shipments(client: TestClient):
    """FARMER gets 403 on consumer tracking endpoint."""
    farmer_token, _ = register_farmer_with_order(client)
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(farmer_token),
    )
    assert resp.status_code == 403


def test_bulk_buyer_cannot_access_consumer_shipments(client: TestClient):
    """BULK_BUYER gets 403."""
    register_user(client, email="bulk@example.com", role="BULK_BUYER")
    token = obtain_token(client, email="bulk@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_financier_cannot_access_consumer_shipments(client: TestClient):
    """FINANCIER gets 403."""
    register_user(client, email="fin@example.com", role="FINANCIER")
    token = obtain_token(client, email="fin@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_logistics_cannot_access_consumer_shipments(client: TestClient):
    """LOGISTICS gets 403."""
    register_user(client, email="log@example.com", role="LOGISTICS")
    token = obtain_token(client, email="log@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_admin_cannot_access_consumer_shipments(client: TestClient):
    """ADMIN gets 403."""
    register_user(client, email="admin_track@example.com", role="ADMIN")
    token = obtain_token(client, email="admin_track@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# OWNERSHIP TESTS
# ---------------------------------------------------------------------------


def test_consumer_can_see_own_shipment(client: TestClient):
    """Consumer can see shipment for their own order."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    assert len(body) >= 1
    assert body[0]["id"] == shipment["id"]


def test_consumer_cannot_see_another_consumers_shipment(client: TestClient):
    """Consumer A cannot see Consumer B's shipment."""
    # Farmer with order from Consumer A
    farmer_token, order = register_farmer_with_order(client, email="farmer_shared@example.com")
    shipment = create_shipment(client, farmer_token, order["id"])

    # Consumer A sees the shipment
    consumer_a_token = obtain_token(client, email="consumer@example.com")
    resp_a = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_a_token),
    )
    assert resp_a.status_code == 200
    assert len(resp_a.json()) >= 1

    # Consumer B (different user) should NOT see the shipment
    register_user(client, email="consumer_b@example.com", name="Consumer B", role="CONSUMER")
    consumer_b_token = obtain_token(client, email="consumer_b@example.com")
    resp_b = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_b_token),
    )
    assert resp_b.status_code == 200
    assert resp_b.json() == []


def test_consumer_gets_404_for_nonexistent_shipment(client: TestClient):
    """Nonexistent shipment returns 404."""
    register_user(client, email="consumer_track@example.com", name="Consumer Track", role="CONSUMER")
    consumer_token = obtain_token(client, email="consumer_track@example.com")
    resp = client.get(
        "/api/consumer/shipments/99999",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 404


def test_consumer_gets_404_for_another_consumers_shipment(client: TestClient):
    """Consumer A cannot access Consumer B's shipment detail."""
    # Farmer with order from Consumer A
    farmer_token, order = register_farmer_with_order(client, email="farmer_shared2@example.com")
    shipment = create_shipment(client, farmer_token, order["id"])

    # Consumer A can access it
    consumer_a_token = obtain_token(client, email="consumer@example.com")
    resp_a = client.get(
        f"/api/consumer/shipments/{shipment['id']}",
        headers=auth_headers(consumer_a_token),
    )
    assert resp_a.status_code == 200

    # Register Consumer B
    register_user(client, email="consumer_b2@example.com", name="Consumer B2", role="CONSUMER")
    consumer_b_token = obtain_token(client, email="consumer_b2@example.com")

    # Consumer B cannot access Consumer A's shipment
    resp_b = client.get(
        f"/api/consumer/shipments/{shipment['id']}",
        headers=auth_headers(consumer_b_token),
    )
    assert resp_b.status_code == 404


# ---------------------------------------------------------------------------
# DATA TESTS
# ---------------------------------------------------------------------------


def test_shipment_status_returned_correctly(client: TestClient):
    """Status is correctly returned in the tracking response."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    assert body[0]["status"] == "PENDING"


def test_pickup_location_returned_correctly(client: TestClient):
    """Pickup location is correctly returned."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    assert body[0]["pickup_location"] == "Farm Gate, Rampur"


def test_destination_returned_correctly(client: TestClient):
    """Destination is correctly returned."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    assert body[0]["destination"] == "City Warehouse, Mumbai"


def test_estimated_delivery_returned_correctly(client: TestClient):
    """Estimated delivery is correctly returned."""
    from datetime import datetime, timezone

    farmer_token, order = register_farmer_with_order(client)
    estimated = datetime(2026, 12, 25, tzinfo=timezone.utc)
    shipment = create_shipment(
        client, farmer_token, order["id"],
        estimated_delivery=estimated,
    )

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    assert body[0]["estimated_delivery"] is not None


def test_order_relationship_works(client: TestClient):
    """Order relationship is correct in the response."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    assert body[0]["order_id"] == order["id"]


def test_shipment_response_contains_required_fields(client: TestClient):
    """Response contains all required tracking fields."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    item = body[0]

    assert "id" in item
    assert "order_id" in item
    assert "produce_name" in item
    assert "crop" in item
    assert "order_status" in item
    assert "status" in item
    assert "pickup_location" in item
    assert "destination" in item
    assert "estimated_delivery" in item
    assert "logistics_cost" in item
    assert "created_at" in item
    assert "updated_at" in item


def test_response_does_not_expose_sensitive_pii(client: TestClient):
    """Response does not expose sensitive farmer information."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    body = resp.json()
    item = body[0]

    sensitive_keys = {"password", "password_hash", "email", "phone", "hashed_password", "documents", "aadhaar", "pan", "bank_details"}
    for key in sensitive_keys:
        assert key not in item, f"Sensitive key '{key}' exposed in shipment response"


def test_single_shipment_detail(client: TestClient):
    """GET /api/consumer/shipments/{id} returns correct shipment detail."""
    farmer_token, order = register_farmer_with_order(client)
    shipment = create_shipment(client, farmer_token, order["id"])

    consumer_token = obtain_token(client, email="consumer@example.com")
    resp = client.get(
        f"/api/consumer/shipments/{shipment['id']}",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == shipment["id"]
    assert body["order_id"] == order["id"]
    assert body["crop"] == "Wheat"
    assert body["status"] == "PENDING"
    assert body["pickup_location"] == "Farm Gate, Rampur"
    assert body["destination"] == "City Warehouse, Mumbai"


# ---------------------------------------------------------------------------
# INTEGRATION TEST
# ---------------------------------------------------------------------------


def _register_and_create_produce(client: TestClient) -> tuple[str, dict]:
    """Helper: register farmer, approve, create produce. Return (token, produce_body)."""
    from tests.test_produce import approve_farmer, create_produce

    register_user(client, email="farmer_integ@example.com", role="FARMER")
    farmer_token = obtain_token(client, email="farmer_integ@example.com")
    approve_farmer(client, farmer_token, farmer_email="farmer_integ@example.com")
    produce_body = create_produce(client, farmer_token, crop="Wheat", quantity=100, price_per_unit=25.0)
    return farmer_token, produce_body


def test_full_marketplace_to_order_to_shipment_to_tracking_flow(client: TestClient):
    """Full flow: order a produce, create a shipment, consumer sees tracking."""
    farmer_token, produce_resp = _register_and_create_produce(client)

    # Consumer places order
    register_user(client, email="consumer_integ@example.com", name="Consumer Integ", role="CONSUMER")
    consumer_token = obtain_token(client, email="consumer_integ@example.com")

    order_resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": produce_resp["id"], "quantity": 5},
    )
    assert order_resp.status_code == 201
    order = order_resp.json()

    # Farmer confirms the order
    client.patch(
        f"/api/orders/{order['id']}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    # Create a shipment for the order
    from app.core.database import SessionLocal
    from app.models.shipment import Shipment
    db = SessionLocal()
    try:
        shipment = Shipment(
            order_id=order["id"],
            status="ASSIGNED",
            pickup_location="Farm Gate, Rampur",
            destination="Consumer Home, Delhi",
            logistics_cost=300.0,
        )
        db.add(shipment)
        db.commit()
        db.refresh(shipment)
    finally:
        db.close()

    # Consumer can see the tracking
    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 1
    assert body[0]["status"] == "ASSIGNED"
    assert body[0]["destination"] == "Consumer Home, Delhi"
    assert body[0]["logistics_cost"] == "300.00"


# ---------------------------------------------------------------------------
# EMPTY LIST TEST
# ---------------------------------------------------------------------------


def test_consumer_gets_empty_shipment_list(client: TestClient):
    """Consumer with no orders/shipments gets empty list."""
    register_user(client, email="consumer_empty@example.com", name="Consumer Empty", role="CONSUMER")
    consumer_token = obtain_token(client, email="consumer_empty@example.com")

    resp = client.get(
        "/api/consumer/shipments",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 200
    assert resp.json() == []
