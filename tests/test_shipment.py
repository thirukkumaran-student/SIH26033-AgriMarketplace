"""Tests for the Farmer Shipment View module.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from decimal import Decimal

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_farmer_with_order(
    client: TestClient,
    email: str = "farmer@example.com",
    quantity: int = 100,
    price_per_unit: float = 25.0,
) -> tuple[str, dict]:
    """Register a farmer, approve them, create a produce listing, and place a CONFIRMED order."""
    register_user(
        client,
        email=email,
        role="FARMER",
    )

    farmer_token = obtain_token(
        client,
        email=email,
    )

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
    register_user(
        client,
        email="admin@example.com",
        role="ADMIN",
    )

    admin_token = obtain_token(
        client,
        email="admin@example.com",
    )

    from app.core.security import decode_access_token

    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )

    assert resp.status_code == 200, resp.text

    # Create produce listing
    produce_resp = client.post(
        "/api/produce",
        headers=auth_headers(farmer_token),
        json={
            "crop": "Wheat",
            "category": "Cereals",
            "quantity": quantity,
            "unit": "kg",
            "price_per_unit": price_per_unit,
            "location": "Village Rampur, UP",
        },
    )

    assert produce_resp.status_code == 201, produce_resp.text

    produce = produce_resp.json()

    # Place order from a consumer
    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )

    consumer_token = obtain_token(
        client,
        email="consumer@example.com",
    )

    order_resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={
            "produce_id": produce["id"],
            "quantity": 10,
        },
    )

    assert order_resp.status_code == 201, order_resp.text

    order = order_resp.json()

    # Confirm the order
    client.patch(
        f"/api/orders/{order['id']}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    return farmer_token, order


def create_shipment(
    client: TestClient,
    farmer_token: str,
    order_id: int,
    **overrides,
) -> dict:
    """Create a shipment for an order. (Direct DB insert since no create endpoint yet)"""
    from app.core.database import SessionLocal
    from app.models.shipment import Shipment

    db = SessionLocal()

    try:
        shipment = Shipment(
            order_id=order_id,
            status="PENDING",
            pickup_location="Farm Gate, Rampur",
            destination="City Warehouse, Mumbai",
            logistics_cost=Decimal("500.00"),
            **overrides,
        )

        db.add(shipment)
        db.commit()
        db.refresh(shipment)

        result = {
            "id": shipment.id,
            "order_id": shipment.order_id,
            "status": shipment.status,
            "pickup_location": shipment.pickup_location,
            "destination": shipment.destination,
            "estimated_delivery": shipment.estimated_delivery,
            "logistics_cost": shipment.logistics_cost,
            "created_at": shipment.created_at,
            "updated_at": shipment.updated_at,
        }

    finally:
        db.close()

    return result


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def test_farmer_authentication_required(client: TestClient):
    resp = client.get("/api/farmer/shipments")

    assert resp.status_code == 401


def test_non_farmer_cannot_access_shipments(client: TestClient):
    register_user(
        client,
        email="consumer@example.com",
        role="CONSUMER",
    )

    token = obtain_token(
        client,
        email="consumer@example.com",
    )

    resp = client.get(
        "/api/farmer/shipments",
        headers=auth_headers(token),
    )

    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# List shipments
# ---------------------------------------------------------------------------


def test_farmer_can_list_their_shipments(client: TestClient):
    farmer_token, order = register_farmer_with_order(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    shipment = create_shipment(
        client,
        farmer_token,
        order["id"],
    )

    resp = client.get(
        "/api/farmer/shipments",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200

    body = resp.json()

    assert len(body) >= 1


def test_farmer_gets_empty_shipment_list(client: TestClient):
    farmer_token, _ = register_farmer_with_order(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    resp = client.get(
        "/api/farmer/shipments",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200

    body = resp.json()

    assert len(body) == 0


def test_farmer_cannot_see_another_farmer_shipment(client: TestClient):
    farmerA_token, order_a = register_farmer_with_order(
        client,
        email="farmerA@example.com",
        quantity=100,
    )

    shipment_a = create_shipment(
        client,
        farmerA_token,
        order_a["id"],
    )

    farmerB_token, order_b = register_farmer_with_order(
        client,
        email="farmerB@example.com",
        quantity=100,
    )

    shipment_b = create_shipment(
        client,
        farmerB_token,
        order_b["id"],
    )

    resp = client.get(
        "/api/farmer/shipments",
        headers=auth_headers(farmerB_token),
    )

    body = resp.json()

    assert len(body) == 1
    assert body[0]["order_id"] == order_b["id"]
    assert body[0]["id"] == shipment_b["id"]


def test_farmers_own_shipment_list_contains_only_their_order_shipments(
    client: TestClient,
):
    farmerA_token, order_a = register_farmer_with_order(
        client,
        email="farmerA@example.com",
        quantity=100,
    )

    shipment_a = create_shipment(
        client,
        farmerA_token,
        order_a["id"],
    )

    farmerB_token, order_b = register_farmer_with_order(
        client,
        email="farmerB@example.com",
        quantity=100,
    )

    resp = client.get(
        "/api/farmer/shipments",
        headers=auth_headers(farmerA_token),
    )

    body = resp.json()

    assert len(body) == 1
    assert body[0]["order_id"] == order_a["id"]
    assert body[0]["id"] == shipment_a["id"]
    assert body[0]["crop"] == "Wheat"


# ---------------------------------------------------------------------------
# Get single shipment
# ---------------------------------------------------------------------------


def test_farmer_can_get_their_own_shipment(client: TestClient):
    farmer_token, order = register_farmer_with_order(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    shipment = create_shipment(
        client,
        farmer_token,
        order["id"],
    )

    resp = client.get(
        f"/api/farmer/shipments/{shipment['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200

    body = resp.json()

    assert body["id"] == shipment["id"]
    assert body["order_id"] == order["id"]
    assert body["crop"] == "Wheat"
    assert body["status"] == "PENDING"


def test_farmer_gets_404_for_nonexistent_shipment(client: TestClient):
    farmer_token, _ = register_farmer_with_order(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    resp = client.get(
        "/api/farmer/shipments/99999",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 404


def test_farmer_gets_404_for_another_farmers_shipment(client: TestClient):
    farmerA_token, order_a = register_farmer_with_order(
        client,
        email="farmerA@example.com",
        quantity=100,
    )

    shipment_a = create_shipment(
        client,
        farmerA_token,
        order_a["id"],
    )

    farmerB_token, order_b = register_farmer_with_order(
        client,
        email="farmerB@example.com",
        quantity=100,
    )

    resp = client.get(
        f"/api/farmer/shipments/{shipment_a['id']}",
        headers=auth_headers(farmerB_token),
    )

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Response schema validation
# ---------------------------------------------------------------------------


def test_shipment_response_schema(client: TestClient):
    farmer_token, order = register_farmer_with_order(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    shipment = create_shipment(
        client,
        farmer_token,
        order["id"],
    )

    resp = client.get(
        "/api/farmer/shipments",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200

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

    from app.core.enums import ShipmentStatus

    assert item["status"] in [
        status.value
        for status in ShipmentStatus
    ]


def test_single_shipment_detail_response(client: TestClient):
    farmer_token, order = register_farmer_with_order(
        client,
        quantity=100,
        price_per_unit=25.0,
    )

    shipment = create_shipment(
        client,
        farmer_token,
        order["id"],
    )

    resp = client.get(
        f"/api/farmer/shipments/{shipment['id']}",
        headers=auth_headers(farmer_token),
    )

    assert resp.status_code == 200

    body = resp.json()

    assert "id" in body
    assert "order_id" in body
    assert "produce_name" in body
    assert "crop" in body
    assert "order_status" in body
    assert "status" in body
    assert "pickup_location" in body
    assert "destination" in body
    assert "estimated_delivery" in body
    assert "logistics_cost" in body
    assert "created_at" in body
    assert "updated_at" in body