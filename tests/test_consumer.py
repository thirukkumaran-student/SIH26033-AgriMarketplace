"""Tests for the Consumer Profile module.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_consumer(client: TestClient, email: str | None = None) -> str:
    """Register a CONSUMER user and return their JWT token."""
    email = email or "consumer@example.com"
    register_user(client, email=email, name="Test Consumer", role="CONSUMER")
    return obtain_token(client, email=email)


def create_consumer_profile(client: TestClient, token: str, **overrides) -> dict:
    """Create a consumer profile and return the response body."""
    payload = {
        "phone": "9876543210",
        "address": "123 Consumer Lane",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
    }
    payload.update(overrides)
    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json=payload,
    )
    return resp.json() if resp.status_code in (200, 201) else resp.json()


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------


def test_consumer_can_create_profile(client: TestClient):
    token = register_consumer(client)
    body = create_consumer_profile(client, token)
    assert body["user_id"] > 0
    assert body["phone"] == "9876543210"
    assert body["city"] == "Mumbai"
    assert body["state"] == "Maharashtra"
    assert body["pincode"] == "400001"
    assert "created_at" in body
    assert "updated_at" in body


def test_consumer_cannot_create_duplicate_profile(client: TestClient):
    token = register_consumer(client)
    first = create_consumer_profile(client, token)
    assert first.get("id") is not None

    second = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "1111111111", "city": "Delhi"},
    )
    assert second.status_code == 409
    assert "already exists" in second.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------


def test_consumer_can_read_own_profile(client: TestClient):
    token = register_consumer(client)
    create_consumer_profile(client, token, city="Chennai", state="Tamil Nadu")
    resp = client.get("/api/consumer/profile", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["city"] == "Chennai"
    assert body["state"] == "Tamil Nadu"


def test_consumer_profile_not_found_if_missing(client: TestClient):
    token = register_consumer(client)
    resp = client.get("/api/consumer/profile", headers=auth_headers(token))
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


def test_consumer_can_update_own_profile(client: TestClient):
    token = register_consumer(client)
    create_consumer_profile(client, token, phone="9876543210", city="Pune")
    resp = client.put(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "1234567890", "address": "45 New Street"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["phone"] == "1234567890"
    assert body["address"] == "45 New Street"
    assert body["city"] == "Pune"  # unchanged


def test_consumer_update_profile_not_found(client: TestClient):
    token = register_consumer(client)
    resp = client.put(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"city": "Goa"},
    )
    assert resp.status_code == 404


def test_consumer_cannot_change_user_id_via_update(client: TestClient):
    token = register_consumer(client)
    body = create_consumer_profile(client, token)
    profile_id = body["id"]
    user_id = body["user_id"]

    resp = client.put(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "1234567890", "user_id": 99999},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["phone"] == "1234567890"
    assert body["user_id"] == user_id  # user_id is not overwritten
    assert body["id"] == profile_id


# ---------------------------------------------------------------------------
# Authorization — non-CONSUMER roles
# ---------------------------------------------------------------------------


def test_farmer_cannot_access_consumer_profile(client: TestClient):
    farmer_token = register_consumer.__wrapped__ if False else None
    # Use explicit helper-free approach: register a farmer directly
    register_user(client, email="farmer_cp@example.com", name="Test Farmer", role="FARMER")
    token = obtain_token(client, email="farmer_cp@example.com")

    endpoints = [
        ("POST", "/api/consumer/profile", {"phone": "111"}),
        ("GET", "/api/consumer/profile", None),
        ("PUT", "/api/consumer/profile", {"city": "Goa"}),
    ]

    for method, path, payload in endpoints:
        kwargs = {"headers": auth_headers(token)}
        if payload is not None:
            kwargs["json"] = payload

        if method == "GET":
            resp = client.get(path, **kwargs)
        elif method == "POST":
            resp = client.post(path, **kwargs)
        else:  # PUT
            resp = client.put(path, **kwargs)

        assert resp.status_code == 403, f"{method} {path} should be 403 for FARMER, got {resp.status_code}"  # noqa: E501


def test_bulk_buyer_cannot_access_consumer_profile(client: TestClient):
    register_user(client, email="bulk_cp@example.com", name="Test Bulk Buyer", role="BULK_BUYER")
    token = obtain_token(client, email="bulk_cp@example.com")

    resp = client.get("/api/consumer/profile", headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "111"},
    )
    assert resp.status_code == 403


def test_financier_cannot_access_consumer_profile(client: TestClient):
    register_user(client, email="fin_cp@example.com", name="Test Financier", role="FINANCIER")
    token = obtain_token(client, email="fin_cp@example.com")

    resp = client.get("/api/consumer/profile", headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "111"},
    )
    assert resp.status_code == 403


def test_logistics_cannot_access_consumer_profile(client: TestClient):
    register_user(client, email="log_cp@example.com", name="Test Logistics", role="LOGISTICS")
    token = obtain_token(client, email="log_cp@example.com")

    resp = client.get("/api/consumer/profile", headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "111"},
    )
    assert resp.status_code == 403


def test_admin_cannot_access_consumer_profile(client: TestClient):
    register_user(client, email="admin_cp@example.com", name="Test Admin", role="ADMIN")
    token = obtain_token(client, email="admin_cp@example.com")

    resp = client.get("/api/consumer/profile", headers=auth_headers(token))
    assert resp.status_code == 403

    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "111"},
    )
    assert resp.status_code == 403


def test_unauthenticated_cannot_access_consumer_profile(client: TestClient):
    endpoints = [
        ("GET", "/api/consumer/profile", None),
        ("POST", "/api/consumer/profile", {"phone": "111"}),
        ("PUT", "/api/consumer/profile", {"city": "Goa"}),
    ]

    for method, path, payload in endpoints:
        kwargs = {}
        if payload is not None:
            kwargs["json"] = payload

        if method == "GET":
            resp = client.get(path, **kwargs)
        elif method == "POST":
            resp = client.post(path, **kwargs)
        else:  # PUT
            resp = client.put(path, **kwargs)

        assert resp.status_code == 401, f"{method} {path} should be 401, got {resp.status_code}"  # noqa: E501


# ---------------------------------------------------------------------------
# Ownership — consumer A cannot access consumer B
# ---------------------------------------------------------------------------


def test_consumer_a_cannot_access_consumer_b_profile(client: TestClient):
    token_a = register_consumer(client, email="consumer_a@example.com")
    token_b = register_consumer(client, email="consumer_b@example.com")

    create_consumer_profile(client, token_b, city="Kolkata")

    resp = client.get("/api/consumer/profile", headers=auth_headers(token_a))
    # Consumer A has no profile, so 404 is expected (not another user's data)
    assert resp.status_code == 404


def test_consumer_a_cannot_update_consumer_b_profile(client: TestClient):
    token_a = register_consumer(client, email="consumer_a@example.com")
    token_b = register_consumer(client, email="consumer_b@example.com")

    # Consumer B creates a profile; consumer A cannot update it because the
    # endpoint is bound to current_user, not to any client-supplied id.
    create_consumer_profile(client, token_b, phone="9876543210")

    resp = client.put(
        "/api/consumer/profile",
        headers=auth_headers(token_a),
        json={"phone": "0000000000"},
    )
    assert resp.status_code == 404  # A has no profile


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_invalid_pincode_too_short_rejected(client: TestClient):
    token = register_consumer(client)
    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"pincode": "12"},
    )
    assert resp.status_code == 422
    assert "Pincode" in resp.json()["detail"][0]["msg"]


def test_blank_phone_rejected(client: TestClient):
    token = register_consumer(client)
    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"phone": "   "},
    )
    assert resp.status_code == 422
    assert "Phone must not be blank" in resp.json()["detail"][0]["msg"]


def test_blank_city_rejected(client: TestClient):
    token = register_consumer(client)
    resp = client.post(
        "/api/consumer/profile",
        headers=auth_headers(token),
        json={"city": "   "},
    )
    assert resp.status_code == 422
    assert "City must not be blank" in resp.json()["detail"][0]["msg"]
