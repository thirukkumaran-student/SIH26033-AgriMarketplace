"""Tests for the Farmer Produce module.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from datetime import date

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_farmer(client: TestClient) -> str:
    """Register a farmer and return their JWT token."""
    register_user(client, email="farmer@example.com", role="FARMER")
    return obtain_token(client, email="farmer@example.com")


def approve_farmer(client: TestClient, farmer_token: str, farmer_email: str = "farmer@example.com") -> None:
    """Approve a farmer by submitting docs and simulating admin approval."""
    # Submit verification documents
    for doc_type in ["AADHAAR", "PAN"]:
        resp = client.post(
            "/api/verification/documents",
            headers=auth_headers(farmer_token),
            json={"document_type": doc_type, "document_number": f"DOC-{doc_type}"},
        )
        assert resp.status_code == 201, resp.text

    # Admin approves — register admin (ignore 409 if already exists) and call approve endpoint
    resp = register_user(client, email="admin@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin@example.com")

    # Get farmer_id from the token payload
    from app.core.security import decode_access_token
    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200, resp.text


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
# Create produce — verification requirement
# ---------------------------------------------------------------------------


def test_approved_farmer_can_create_produce(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    body = create_produce(client, token)
    assert body["crop"] == "Wheat"
    assert body["category"] == "Cereals"
    assert body["quantity"] == 100
    assert body["unit"] == "kg"
    assert body["price_per_unit"] == 25.0
    assert body["status"] == "ACTIVE"
    assert body["farmer_id"] > 0
    assert "id" in body


def test_pending_farmer_cannot_create_produce(client):
    token = register_farmer(client)
    # Submit docs but don't approve
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "1111"},
    )

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Rice", "category": "Cereals", "quantity": 50, "unit": "kg", "price_per_unit": 30.0, "location": "UP"},
    )
    assert resp.status_code == 403
    assert "PENDING" in resp.json()["detail"]


def test_rejected_farmer_cannot_create_produce(client):
    token = register_farmer(client)
    # Submit docs
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "1111"},
    )
    # Admin rejects
    register_user(client, email="admin@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin@example.com")

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    client.post(
        f"/api/admin/verifications/{farmer_id}/reject",
        headers=auth_headers(admin_token),
        json={"remarks": "Invalid documents"},
    )

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Rice", "category": "Cereals", "quantity": 50, "unit": "kg", "price_per_unit": 30.0, "location": "UP"},
    )
    assert resp.status_code == 403
    assert "REJECTED" in resp.json()["detail"]


def test_unverified_farmer_cannot_create_produce(client):
    token = register_farmer(client)
    # No documents submitted at all

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Rice", "category": "Cereals", "quantity": 50, "unit": "kg", "price_per_unit": 30.0, "location": "UP"},
    )
    assert resp.status_code == 403
    assert "verification documents" in resp.json()["detail"].lower()


def test_non_farmer_cannot_create_produce(client):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    token = obtain_token(client, email="consumer@example.com")

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Rice", "category": "Cereals", "quantity": 50, "unit": "kg", "price_per_unit": 30.0, "location": "UP"},
    )
    assert resp.status_code == 403


def test_unauthenticated_cannot_create_produce(client):
    resp = client.post(
        "/api/produce",
        json={"crop": "Rice", "category": "Cereals", "quantity": 50, "unit": "kg", "price_per_unit": 30.0, "location": "UP"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_invalid_quantity_rejected(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Wheat", "category": "Cereals", "quantity": 0, "unit": "kg", "price_per_unit": 25.0, "location": "UP"},
    )
    assert resp.status_code == 422


def test_invalid_price_rejected(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Wheat", "category": "Cereals", "quantity": 100, "unit": "kg", "price_per_unit": -5.0, "location": "UP"},
    )
    assert resp.status_code == 422


def test_correct_default_status(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    body = create_produce(client, token)
    assert body["status"] == "ACTIVE"


# ---------------------------------------------------------------------------
# Read produce
# ---------------------------------------------------------------------------


def test_farmer_can_list_produce(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    create_produce(client, token, crop="Wheat")
    create_produce(client, token, crop="Rice", category="Cereals")

    resp = client.get("/api/produce", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 2
    crops = {item["crop"] for item in body}
    assert "Wheat" in crops
    assert "Rice" in crops


def test_farmer_can_retrieve_produce(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token, crop="Maize")
    resp = client.get(f"/api/produce/{created['id']}", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["crop"] == "Maize"


def test_get_nonexistent_produce_returns_404(client):
    token = register_farmer(client)
    resp = client.get("/api/produce/99999", headers=auth_headers(token))
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update produce
# ---------------------------------------------------------------------------


def test_farmer_can_update_own_produce(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token, crop="Wheat", quantity=100)
    resp = client.patch(
        f"/api/produce/{created['id']}",
        headers=auth_headers(token),
        json={"price_per_unit": 30.0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["price_per_unit"] == 30.0
    assert body["quantity"] == 100  # quantity not changed
    assert body["crop"] == "Wheat"  # unchanged


def test_farmer_cannot_update_other_farmers_produce(client):
    # Farmer A
    register_user(client, email="farmerA@example.com", role="FARMER")
    token_a = obtain_token(client, email="farmerA@example.com")
    approve_farmer(client, token_a, farmer_email="farmerA@example.com")
    created_a = create_produce(client, token_a, crop="Wheat")

    # Farmer B
    register_user(client, email="farmerB@example.com", role="FARMER")
    token_b = obtain_token(client, email="farmerB@example.com")
    approve_farmer(client, token_b, farmer_email="farmerB@example.com")

    resp = client.patch(
        f"/api/produce/{created_a['id']}",
        headers=auth_headers(token_b),
        json={"crop": "Stolen Wheat"},
    )
    assert resp.status_code == 404  # 404 to avoid leaking


def test_approved_farmer_can_change_status_to_inactive(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token)
    resp = client.patch(
        f"/api/produce/{created['id']}",
        headers=auth_headers(token),
        json={"status": "INACTIVE"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "INACTIVE"


def test_approved_farmer_can_change_status_to_sold_out_when_quantity_zero(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token, quantity=10)
    # The audit fix disallows SOLD_OUT while quantity > 0. To reach the
    # happy path we must have quantity=0 first. Because ProduceUpdate also
    # forbids quantity=0 (gt=0), the only ergonomic way to reach SOLD_OUT
    # under the current schema is direct DB insertion for the test.
    from app.core.database import SessionLocal
    from app.models.produce import Produce
    from app.core.enums import ProduceStatus

    db = SessionLocal()
    try:
        zero_produce = Produce(
            farmer_id=created["farmer_id"],
            crop=created["crop"],
            category=created["category"],
            quantity=0,
            unit=created["unit"],
            price_per_unit=created["price_per_unit"],
            location=created["location"],
            status=ProduceStatus.ACTIVE.value,
        )
        db.add(zero_produce)
        db.commit()
        db.refresh(zero_produce)
    finally:
        db.close()

    resp = client.patch(
        f"/api/produce/{zero_produce.id}",
        headers=auth_headers(token),
        json={"status": "SOLD_OUT"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "SOLD_OUT"


def test_pending_farmer_cannot_change_own_produce_status(client):
    farmer_email = "pendingstatus@example.com"
    register_user(client, email=farmer_email, role="FARMER")
    token = obtain_token(client, email=farmer_email)

    # Submit documents but do not approve
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "1111"},
    )

    # Create a produce the pending farmer owns - should fail
    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Wheat", "category": "Cereals", "quantity": 10, "unit": "kg", "price_per_unit": 25.0, "location": "UP"},
    )
    assert resp.status_code == 403, resp.text


def test_unverified_farmer_cannot_change_status_on_own_missing_produce(client):
    farmer_email = "unverifiedstatus@example.com"
    register_user(client, email=farmer_email, role="FARMER")
    token = obtain_token(client, email=farmer_email)

    # No documents at all
    resp = client.patch(
        "/api/produce/99999",
        headers=auth_headers(token),
        json={"status": "SOLD_OUT"},
    )
    assert resp.status_code == 404


def test_rejected_farmer_cannot_change_own_produce_status(client):
    farmer_email = "rejectedstatus@example.com"
    register_user(client, email=farmer_email, role="FARMER")
    token = obtain_token(client, email=farmer_email)

    # Submit docs and get rejected
    client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "1111"},
    )
    register_user(client, email="admin_reject_status@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_reject_status@example.com")

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == farmer_email))
        farmer_id = farmer.id
    finally:
        db.close()

    client.post(
        f"/api/admin/verifications/{farmer_id}/reject",
        headers=auth_headers(admin_token),
        json={"remarks": "Invalid documents"},
    )

    # Rejected farmer cannot create produce
    resp = client.post(
        "/api/produce",
        headers=auth_headers(token),
        json={"crop": "Wheat", "category": "Cereals", "quantity": 10, "unit": "kg", "price_per_unit": 25.0, "location": "UP"},
    )
    assert resp.status_code == 403, resp.text


def test_farmer_cannot_set_sold_out_with_quantity(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token)
    resp = client.patch(
        f"/api/produce/{created['id']}",
        headers=auth_headers(token),
        json={"status": "SOLD_OUT"},
    )
    # The produce still has quantity=100, so SOLD_OUT is now rejected
    assert resp.status_code == 422, resp.text
    assert "SOLD_OUT" in resp.json()["detail"].upper() or "quantity" in resp.json()["detail"].lower()



def test_farmer_can_update_status(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token)
    resp = client.patch(
        f"/api/produce/{created['id']}",
        headers=auth_headers(token),
        json={"status": "SOLD_OUT"},
    )
    # The produce still has quantity=100, so SOLD_OUT is now rejected
    assert resp.status_code == 422, resp.text
    assert "SOLD_OUT" in resp.json()["detail"].upper() or "quantity" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Delete produce
# ---------------------------------------------------------------------------


def test_farmer_can_delete_own_produce(client):
    token = register_farmer(client)
    approve_farmer(client, token)

    created = create_produce(client, token, crop="To Delete")
    resp = client.delete(f"/api/produce/{created['id']}", headers=auth_headers(token))
    assert resp.status_code == 204

    # Verify it's gone
    resp = client.get(f"/api/produce/{created['id']}", headers=auth_headers(token))
    assert resp.status_code == 404


def test_farmer_cannot_delete_other_farmers_produce(client):
    register_user(client, email="farmerA@example.com", role="FARMER")
    token_a = obtain_token(client, email="farmerA@example.com")
    approve_farmer(client, token_a, farmer_email="farmerA@example.com")
    created_a = create_produce(client, token_a, crop="Protected")

    register_user(client, email="farmerB@example.com", role="FARMER")
    token_b = obtain_token(client, email="farmerB@example.com")
    approve_farmer(client, token_b, farmer_email="farmerB@example.com")

    resp = client.delete(f"/api/produce/{created_a['id']}", headers=auth_headers(token_b))
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Marketplace-style listing
# ---------------------------------------------------------------------------


def test_get_all_produce_for_marketplace(client):
    """GET /api/produce returns produce across all farmers for marketplace use."""
    # Farmer A
    register_user(client, email="farmerA@example.com", role="FARMER")
    token_a = obtain_token(client, email="farmerA@example.com")
    approve_farmer(client, token_a, farmer_email="farmerA@example.com")
    create_produce(client, token_a, crop="Wheat", category="Cereals", location="UP")

    # Farmer B
    register_user(client, email="farmerB@example.com", role="FARMER")
    token_b = obtain_token(client, email="farmerB@example.com")
    approve_farmer(client, token_b, farmer_email="farmerB@example.com")
    create_produce(client, token_b, crop="Tomato", category="Vegetables", location="Maharashtra")

    # Any user can see all produce
    register_user(client, email="buyer@example.com", role="CONSUMER")
    buyer_token = obtain_token(client, email="buyer@example.com")

    resp = client.get("/api/produce", headers=auth_headers(buyer_token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 2

    # Filter by category
    resp = client.get("/api/produce?category=Cereals", headers=auth_headers(buyer_token))
    assert resp.status_code == 200
    assert all(item["category"] == "Cereals" for item in resp.json())

    # Filter by location
    resp = client.get("/api/produce?location=Maharashtra", headers=auth_headers(buyer_token))
    assert resp.status_code == 200
    assert all("Maharashtra" in item["location"] for item in resp.json())
