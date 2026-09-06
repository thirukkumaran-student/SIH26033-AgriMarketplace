"""Tests for the Consumer Marketplace Module.

Run from the backend/ directory: pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.enums import ProduceStatus
from app.core.security import decode_access_token
from app.models.produce import Produce
from tests.test_auth import auth_headers, obtain_token, register_user
from tests.test_consumer import register_consumer
from tests.test_produce import approve_farmer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_user_id(token: str) -> int:
    """Extract user_id from a JWT access token."""
    payload = decode_access_token(token)
    return int(payload["sub"])


def insert_produce_db(
    farmer_id: int,
    crop: str = "Wheat",
    category: str = "Cereals",
    quantity: int = 100,
    unit: str = "kg",
    price_per_unit: float = 25.0,
    location: str = "Punjab, India",
    status: str = ProduceStatus.ACTIVE.value,
    harvest_date=None,
    quality_grade: str = "Grade A",
    image: str | None = None,
) -> Produce:
    """Directly insert a produce record into the database for test setup."""
    db = SessionLocal()
    try:
        produce = Produce(
            farmer_id=farmer_id,
            crop=crop,
            category=category,
            quantity=quantity,
            unit=unit,
            price_per_unit=price_per_unit,
            location=location,
            status=status,
            harvest_date=harvest_date,
            quality_grade=quality_grade,
            image=image,
        )
        db.add(produce)
        db.commit()
        db.refresh(produce)
        return produce
    finally:
        db.close()


def setup_approved_farmer(client: TestClient, email: str = "approved_farmer@example.com") -> tuple[str, int]:
    """Register and approve a farmer, returning (token, farmer_id)."""
    register_user(client, email=email, role="FARMER")
    token = obtain_token(client, email=email)
    approve_farmer(client, token, farmer_email=email)
    return token, get_user_id(token)


def setup_unverified_farmer(client: TestClient, email: str = "unverified_farmer@example.com") -> tuple[str, int]:
    """Register a farmer without submitting any verification documents."""
    register_user(client, email=email, role="FARMER")
    token = obtain_token(client, email=email)
    return token, get_user_id(token)


def setup_pending_farmer(client: TestClient, email: str = "pending_farmer@example.com") -> tuple[str, int]:
    """Register a farmer and submit documents without admin approval."""
    register_user(client, email=email, role="FARMER")
    token = obtain_token(client, email=email)
    resp = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "PENDING-1234"},
    )
    assert resp.status_code == 201, resp.text
    return token, get_user_id(token)


def setup_rejected_farmer(client: TestClient, email: str = "rejected_farmer@example.com") -> tuple[str, int]:
    """Register a farmer and have an admin reject their verification."""
    register_user(client, email=email, role="FARMER")
    token = obtain_token(client, email=email)
    doc_resp = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "REJECTED-1234"},
    )
    assert doc_resp.status_code == 201, doc_resp.text
    doc_id = doc_resp.json()["id"]
    farmer_id = get_user_id(token)

    # Register admin and reject the document
    register_user(client, email="admin_verifier@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_verifier@example.com")
    reject_resp = client.post(
        f"/api/admin/verifications/{farmer_id}/reject",
        headers=auth_headers(admin_token),
        json={"document_id": doc_id, "remarks": "Forged document"},
    )
    assert reject_resp.status_code == 200, reject_resp.text
    return token, farmer_id


# ---------------------------------------------------------------------------
# 1. AUTHORIZATION TESTS
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_access_marketplace_listing(client: TestClient):
    """Unauthenticated request to list produce returns 401."""
    resp = client.get("/api/marketplace/produce")
    assert resp.status_code == 401


def test_unauthenticated_cannot_access_marketplace_detail(client: TestClient):
    """Unauthenticated request to produce detail returns 401."""
    resp = client.get("/api/marketplace/produce/1")
    assert resp.status_code == 401


def test_consumer_can_access_marketplace(client: TestClient):
    """Authenticated CONSUMER can access marketplace produce list."""
    consumer_token = register_consumer(client)
    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_farmer_cannot_access_marketplace(client: TestClient):
    """FARMER role receives 403 on marketplace endpoints."""
    register_user(client, email="farmer_forbidden@example.com", role="FARMER")
    token = obtain_token(client, email="farmer_forbidden@example.com")

    resp_list = client.get("/api/marketplace/produce", headers=auth_headers(token))
    assert resp_list.status_code == 403

    resp_detail = client.get("/api/marketplace/produce/1", headers=auth_headers(token))
    assert resp_detail.status_code == 403


def test_bulk_buyer_can_access_marketplace(client: TestClient):
    """BULK_BUYER can access the shared marketplace."""
    register_user(
        client,
        email="buyer_marketplace@example.com",
        name="Test Bulk Buyer",
        role="BULK_BUYER",
    )
    token = obtain_token(client, email="buyer_marketplace@example.com")

    response = client.get(
        "/api/marketplace/produce",
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_bulk_buyer_can_access_marketplace_detail(client: TestClient):
    """BULK_BUYER passes marketplace detail authorization."""
    register_user(
        client,
        email="buyer_marketplace_detail@example.com",
        name="Test Bulk Buyer",
        role="BULK_BUYER",
    )
    token = obtain_token(
        client,
        email="buyer_marketplace_detail@example.com",
    )

    response = client.get(
        "/api/marketplace/produce/1",
        headers=auth_headers(token),
    )

    # Produce 1 may not exist in this isolated test database.
    # 404 means authorization succeeded; 403 means role was rejected.
    assert response.status_code != 403


def test_financier_cannot_access_marketplace(client: TestClient):
    """FINANCIER role receives 403 on marketplace endpoints."""
    register_user(client, email="financier_forbidden@example.com", role="FINANCIER")
    token = obtain_token(client, email="financier_forbidden@example.com")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(token))
    assert resp.status_code == 403


def test_logistics_cannot_access_marketplace(client: TestClient):
    """LOGISTICS role receives 403 on marketplace endpoints."""
    register_user(client, email="logistics_forbidden@example.com", role="LOGISTICS")
    token = obtain_token(client, email="logistics_forbidden@example.com")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_cannot_access_marketplace(client: TestClient):
    """ADMIN role receives 403 on marketplace endpoints (Marketplace is CONSUMER only)."""
    register_user(client, email="admin_forbidden@example.com", role="ADMIN")
    token = obtain_token(client, email="admin_forbidden@example.com")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 2. LISTING ELIGIBILITY TESTS
# ---------------------------------------------------------------------------


def test_approved_farmer_active_positive_quantity_produce_is_visible(client: TestClient):
    """Produce with APPROVED farmer + ACTIVE status + quantity > 0 is visible in marketplace."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    p = insert_produce_db(farmer_id=farmer_id, crop="Basmati Rice", quantity=50, status="ACTIVE")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    listing = resp.json()
    assert len(listing) == 1
    assert listing[0]["id"] == p.id
    assert listing[0]["crop"] == "Basmati Rice"


def test_unverified_farmer_produce_is_hidden(client: TestClient):
    """Produce from an unverified farmer (no verification docs) is NOT visible."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_unverified_farmer(client)

    insert_produce_db(farmer_id=farmer_id, crop="Unverified Wheat", quantity=100, status="ACTIVE")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_pending_farmer_produce_is_hidden(client: TestClient):
    """Produce from a pending farmer is NOT visible."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_pending_farmer(client)

    insert_produce_db(farmer_id=farmer_id, crop="Pending Corn", quantity=100, status="ACTIVE")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_rejected_farmer_produce_is_hidden(client: TestClient):
    """Produce from a rejected farmer is NOT visible."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_rejected_farmer(client)

    insert_produce_db(farmer_id=farmer_id, crop="Rejected Barley", quantity=100, status="ACTIVE")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_inactive_produce_is_hidden(client: TestClient):
    """Produce with status INACTIVE is NOT visible, even if farmer is approved."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    insert_produce_db(farmer_id=farmer_id, crop="Inactive Soybean", quantity=100, status="INACTIVE")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert resp.json() == []


def test_zero_stock_produce_is_hidden(client: TestClient):
    """Produce with quantity 0 is NOT visible, even if farmer is approved and status is ACTIVE."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    insert_produce_db(farmer_id=farmer_id, crop="Sold Out Mustard", quantity=0, status="ACTIVE")

    resp = client.get("/api/marketplace/produce", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# 3. DETAIL ENDPOINT TESTS
# ---------------------------------------------------------------------------


def test_eligible_produce_detail_success(client: TestClient):
    """Eligible produce returns 200 and matches detail schema."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    p = insert_produce_db(
        farmer_id=farmer_id,
        crop="Cotton",
        category="Fiber",
        quantity=80,
        unit="kg",
        price_per_unit=45.5,
        location="Surat, Gujarat",
        status="ACTIVE",
    )

    resp = client.get(f"/api/marketplace/produce/{p.id}", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == p.id
    assert data["crop"] == "Cotton"
    assert data["category"] == "Fiber"
    assert data["quantity"] == 80
    assert data["price_per_unit"] == 45.5
    assert data["location"] == "Surat, Gujarat"
    assert data["status"] == "ACTIVE"


def test_nonexistent_produce_detail_returns_404(client: TestClient):
    """Nonexistent produce ID returns 404."""
    consumer_token = register_consumer(client)
    resp = client.get("/api/marketplace/produce/999999", headers=auth_headers(consumer_token))
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_ineligible_produce_detail_returns_404(client: TestClient):
    """Ineligible produce (inactive, 0 quantity, or non-approved farmer) returns 404."""
    consumer_token = register_consumer(client)
    _, approved_id = setup_approved_farmer(client)
    _, unverified_id = setup_unverified_farmer(client, email="unver_detail@example.com")
    _, pending_id = setup_pending_farmer(client, email="pend_detail@example.com")
    _, rejected_id = setup_rejected_farmer(client, email="rej_detail@example.com")

    # Inactive
    p_inactive = insert_produce_db(approved_id, crop="Inactive", status="INACTIVE", quantity=100)
    # Zero stock
    p_zero = insert_produce_db(approved_id, crop="Zero", status="ACTIVE", quantity=0)
    # Unverified farmer
    p_unverified = insert_produce_db(unverified_id, crop="Unverified", status="ACTIVE", quantity=100)
    # Pending farmer
    p_pending = insert_produce_db(pending_id, crop="Pending", status="ACTIVE", quantity=100)
    # Rejected farmer
    p_rejected = insert_produce_db(rejected_id, crop="Rejected", status="ACTIVE", quantity=100)

    for p in [p_inactive, p_zero, p_unverified, p_pending, p_rejected]:
        resp = client.get(f"/api/marketplace/produce/{p.id}", headers=auth_headers(consumer_token))
        assert resp.status_code == 404, f"Expected 404 for produce id {p.id} with crop {p.crop}"


# ---------------------------------------------------------------------------
# 4. FILTERING TESTS
# ---------------------------------------------------------------------------


def test_filter_by_crop(client: TestClient):
    """Filtering by crop performs case-insensitive substring match."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    insert_produce_db(farmer_id, crop="Golden Wheat", quantity=50)
    insert_produce_db(farmer_id, crop="Organic Wheat Flour", quantity=30)
    insert_produce_db(farmer_id, crop="Basmati Rice", quantity=70)

    # Filter for 'wheat' (case-insensitive)
    resp = client.get("/api/marketplace/produce?crop=wheat", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    crops = [item["crop"] for item in resp.json()]
    assert "Golden Wheat" in crops
    assert "Organic Wheat Flour" in crops
    assert "Basmati Rice" not in crops

    # Filter for 'rice'
    resp_rice = client.get("/api/marketplace/produce?crop=rice", headers=auth_headers(consumer_token))
    assert resp_rice.status_code == 200
    crops_rice = [item["crop"] for item in resp_rice.json()]
    assert crops_rice == ["Basmati Rice"]


def test_filter_by_location(client: TestClient):
    """Filtering by location performs case-insensitive substring match."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    insert_produce_db(farmer_id, crop="Wheat", location="Ludhiana, Punjab")
    insert_produce_db(farmer_id, crop="Rice", location="Karnal, Haryana")

    resp = client.get("/api/marketplace/produce?location=punjab", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert "Punjab" in results[0]["location"]


def test_filter_by_max_price(client: TestClient):
    """Filtering by max_price returns only items with price_per_unit <= max_price."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    insert_produce_db(farmer_id, crop="Budget Wheat", price_per_unit=20.0)
    insert_produce_db(farmer_id, crop="Standard Wheat", price_per_unit=45.0)
    insert_produce_db(farmer_id, crop="Premium Wheat", price_per_unit=90.0)

    resp = client.get("/api/marketplace/produce?max_price=45.0", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    prices = [item["price_per_unit"] for item in resp.json()]
    assert len(prices) == 2
    assert 20.0 in prices
    assert 45.0 in prices
    assert 90.0 not in prices


def test_filter_combined(client: TestClient):
    """Query filters (crop, location, max_price) can be combined conjunctively."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    # 1. Matches all criteria
    target = insert_produce_db(farmer_id, crop="Sharbati Wheat", location="Bhopal, MP", price_per_unit=30.0)
    # 2. Crop mismatch
    insert_produce_db(farmer_id, crop="Basmati Rice", location="Bhopal, MP", price_per_unit=30.0)
    # 3. Location mismatch
    insert_produce_db(farmer_id, crop="Sharbati Wheat", location="Amritsar, Punjab", price_per_unit=30.0)
    # 4. Price mismatch
    insert_produce_db(farmer_id, crop="Sharbati Wheat", location="Bhopal, MP", price_per_unit=80.0)

    resp = client.get(
        "/api/marketplace/produce?crop=wheat&location=bhopal&max_price=40.0",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["id"] == target.id
    assert results[0]["crop"] == "Sharbati Wheat"


# ---------------------------------------------------------------------------
# 5. DATA SAFETY TESTS
# ---------------------------------------------------------------------------


def test_marketplace_response_schema_and_sensitive_data(client: TestClient):
    """Marketplace response contains only consumer-facing produce fields and NO farmer PII."""
    consumer_token = register_consumer(client)
    _, farmer_id = setup_approved_farmer(client)

    p = insert_produce_db(
        farmer_id=farmer_id,
        crop="Organic Millet",
        category="Millets",
        quantity=60,
        unit="kg",
        price_per_unit=55.0,
        location="Jaipur, Rajasthan",
        quality_grade="Grade A+",
        image="http://example.com/millet.jpg",
    )

    resp = client.get(f"/api/marketplace/produce/{p.id}", headers=auth_headers(consumer_token))
    assert resp.status_code == 200
    item = resp.json()

    # Allowed / expected marketplace fields
    expected_fields = {
        "id",
        "crop",
        "category",
        "quantity",
        "unit",
        "price_per_unit",
        "location",
        "harvest_date",
        "quality_grade",
        "image",
        "status",
    }
    assert set(item.keys()) == expected_fields

    # Sensitive farmer data MUST NOT be exposed
    sensitive_keys = {
        "farmer_id",
        "user_id",
        "farmer_name",
        "phone",
        "email",
        "password",
        "hashed_password",
        "documents",
        "aadhaar",
        "pan",
    }
    for key in sensitive_keys:
        assert key not in item, f"Sensitive key '{key}' was exposed in marketplace response!"


def test_marketplace_does_not_accept_farmer_id_override(client: TestClient):
    """Marketplace does not determine ownership/eligibility from client-supplied farmer_id."""
    consumer_token = register_consumer(client)
    _, approved_id = setup_approved_farmer(client)
    _, unverified_id = setup_unverified_farmer(client, email="fake_override@example.com")

    # An unverified farmer's produce
    p_unverified = insert_produce_db(unverified_id, crop="Secret Crop", quantity=100)

    # Client tries to pass farmer_id pointing to the approved farmer to spoof eligibility
    resp = client.get(
        f"/api/marketplace/produce?farmer_id={approved_id}",
        headers=auth_headers(consumer_token),
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()]
    assert p_unverified.id not in ids

    # Detail endpoint also rejects ineligible produce regardless of client query params
    detail_resp = client.get(
        f"/api/marketplace/produce/{p_unverified.id}?farmer_id={approved_id}",
        headers=auth_headers(consumer_token),
    )
    assert detail_resp.status_code == 404
