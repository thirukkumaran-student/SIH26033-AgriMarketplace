"""Tests for the Bulk Buyer Profile module."""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


def register_buyer(client: TestClient, email: str = "buyer@example.com") -> str:
    """Register a BULK_BUYER and return its JWT token."""
    register_user(
        client,
        email=email,
        name="Test Bulk Buyer",
        role="BULK_BUYER",
    )
    return obtain_token(client, email=email)


def create_buyer_profile(
    client: TestClient,
    token: str,
    **overrides,
) -> dict:
    """Create a buyer profile and return the response body."""
    payload = {
        "phone": "9876543210",
        "address": "123 Buyer Lane",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "financing_preference": "NONE",
    }
    payload.update(overrides)

    response = client.post(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json=payload,
    )
    return response.json()


def test_bulk_buyer_can_create_profile(client: TestClient):
    token = register_buyer(client)

    response = client.post(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={
            "phone": "9876543210",
            "address": "123 Buyer Lane",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "financing_preference": "PLATFORM",
        },
    )

    assert response.status_code == 201, response.text

    body = response.json()
    assert body["user_id"] > 0
    assert body["phone"] == "9876543210"
    assert body["city"] == "Mumbai"
    assert body["financing_preference"] == "PLATFORM"
    assert "created_at" in body
    assert "updated_at" in body


def test_bulk_buyer_cannot_create_duplicate_profile(client: TestClient):
    token = register_buyer(client)
    first = create_buyer_profile(client, token)

    assert first["id"] > 0

    response = client.post(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={"city": "Delhi"},
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_bulk_buyer_can_read_own_profile(client: TestClient):
    token = register_buyer(client)

    create_buyer_profile(
        client,
        token,
        city="Chennai",
        state="Tamil Nadu",
        financing_preference="PLATFORM",
    )

    response = client.get(
        "/api/buyer/profile",
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body["city"] == "Chennai"
    assert body["state"] == "Tamil Nadu"
    assert body["financing_preference"] == "PLATFORM"


def test_bulk_buyer_profile_not_found_if_missing(client: TestClient):
    token = register_buyer(client)

    response = client.get(
        "/api/buyer/profile",
        headers=auth_headers(token),
    )

    assert response.status_code == 404


def test_bulk_buyer_can_update_own_profile(client: TestClient):
    token = register_buyer(client)

    create_buyer_profile(
        client,
        token,
        city="Pune",
        financing_preference="NONE",
    )

    response = client.put(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={
            "phone": "1234567890",
            "address": "45 New Street",
            "financing_preference": "PLATFORM",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body["phone"] == "1234567890"
    assert body["address"] == "45 New Street"
    assert body["city"] == "Pune"
    assert body["financing_preference"] == "PLATFORM"


def test_bulk_buyer_update_profile_not_found(client: TestClient):
    token = register_buyer(client)

    response = client.put(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={"city": "Goa"},
    )

    assert response.status_code == 404


def test_bulk_buyer_empty_update_rejected(client: TestClient):
    token = register_buyer(client)
    create_buyer_profile(client, token)

    response = client.put(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={},
    )

    assert response.status_code == 422


def test_bulk_buyer_cannot_change_user_id(client: TestClient):
    token = register_buyer(client)
    body = create_buyer_profile(client, token)

    response = client.put(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={
            "phone": "1234567890",
            "user_id": 99999,
        },
    )

    assert response.status_code == 200

    updated = response.json()
    assert updated["user_id"] == body["user_id"]
    assert updated["id"] == body["id"]


def test_consumer_cannot_access_buyer_profile(client: TestClient):
    register_user(
        client,
        email="consumer_buyer_test@example.com",
        name="Test Consumer",
        role="CONSUMER",
    )
    token = obtain_token(client, email="consumer_buyer_test@example.com")

    response = client.get(
        "/api/buyer/profile",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_financier_cannot_access_buyer_profile(client: TestClient):
    register_user(
        client,
        email="financier_buyer_test@example.com",
        name="Test Financier",
        role="FINANCIER",
    )
    token = obtain_token(client, email="financier_buyer_test@example.com")

    response = client.get(
        "/api/buyer/profile",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_unauthenticated_cannot_access_buyer_profile(client: TestClient):
    response = client.get("/api/buyer/profile")

    assert response.status_code == 401


def test_blank_buyer_phone_rejected(client: TestClient):
    token = register_buyer(client)

    response = client.post(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={"phone": "   "},
    )

    assert response.status_code == 422
    assert "must not be blank" in response.json()["detail"][0]["msg"]


def test_blank_buyer_city_rejected(client: TestClient):
    token = register_buyer(client)

    response = client.post(
        "/api/buyer/profile",
        headers=auth_headers(token),
        json={"city": "   "},
    )

    assert response.status_code == 422
    assert "must not be blank" in response.json()["detail"][0]["msg"]