"""Tests for the shared authentication + RBAC foundation.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_user(
    client: TestClient,
    *,
    email: str = "farmer@example.com",
    password: str = "password123",
    name: str = "Test Farmer",
    role: str = "FARMER",
):
    return client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )


def login_user(
    client: TestClient,
    *,
    email: str = "farmer@example.com",
    password: str = "password123",
):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def obtain_token(
    client: TestClient,
    *,
    email: str = "farmer@example.com",
    password: str = "password123",
) -> str:
    """Register (if needed via caller) then login and return the JWT."""
    response = login_user(client, email=email, password=password)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def get_user_from_db(email: str) -> User | None:
    db = SessionLocal()
    try:
        return db.scalar(select(User).where(User.email == email))
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_farmer(client):
    response = register_user(client)
    assert response.status_code == 201, response.text

    body = response.json()
    assert body["name"] == "Test Farmer"
    assert body["email"] == "farmer@example.com"
    assert body["role"] == "FARMER"
    assert isinstance(body["id"], int)
    assert "created_at" in body

    # The password hash must never be returned by the API.
    assert "password_hash" not in body


def test_register_consumer(client):
    response = register_user(
        client, email="consumer@example.com", name="Test Consumer", role="CONSUMER"
    )
    assert response.status_code == 201, response.text
    assert response.json()["role"] == "CONSUMER"


def test_register_admin(client):
    response = register_user(
        client, email="admin@example.com", name="Test Admin", role="ADMIN"
    )
    assert response.status_code == 201, response.text
    assert response.json()["role"] == "ADMIN"


def test_duplicate_email_is_rejected(client):
    first = register_user(client)
    assert first.status_code == 201

    duplicate = register_user(client, name="Another Farmer")
    assert duplicate.status_code == 409
    assert "registered" in duplicate.json()["detail"].lower()


def test_password_is_stored_hashed_not_plaintext(client):
    password = "password123"
    response = register_user(client, email="farmer@example.com", password=password)
    assert response.status_code == 201, response.text

    user = get_user_from_db("farmer@example.com")
    assert user is not None
    assert user.password_hash != password
    assert user.password_hash.startswith("$2b$")  # bcrypt marker
    assert verify_password(password, user.password_hash) is True
    assert verify_password("wrong-password", user.password_hash) is False


def test_register_normalizes_email(client):
    response = register_user(client, email="  Farmer@Example.COM  ")
    assert response.status_code == 201, response.text
    assert response.json()["email"] == "farmer@example.com"


def test_register_rejects_invalid_role(client):
    response = register_user(client, role="SUPERHERO")
    assert response.status_code == 422


def test_register_rejects_short_password(client):
    response = register_user(client, password="short")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login + JWT
# ---------------------------------------------------------------------------


def test_login_succeeds_with_correct_password(client):
    register_user(client)
    response = login_user(client)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "farmer@example.com"
    assert body["user"]["role"] == "FARMER"
    assert "password_hash" not in body["user"]


def test_login_fails_with_wrong_password(client):
    register_user(client)
    wrong_password = login_user(client, password="not-the-password")
    assert wrong_password.status_code == 401

    unknown_email = login_user(client, email="nobody@example.com")
    assert unknown_email.status_code == 401

    # Same generic message in both cases -> no user/email enumeration.
    assert wrong_password.json()["detail"] == unknown_email.json()["detail"]


def test_login_returns_jwt_with_identity_and_role(client):
    register_user(client)
    token = obtain_token(client)

    payload = decode_access_token(token)
    assert payload["role"] == "FARMER"

    user = get_user_from_db("farmer@example.com")
    assert user is not None
    assert payload["sub"] == str(user.id)


# ---------------------------------------------------------------------------
# Current user endpoint
# ---------------------------------------------------------------------------


def test_me_works_with_valid_jwt(client):
    register_user(client)
    token = obtain_token(client)

    response = client.get("/api/auth/me", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["email"] == "farmer@example.com"
    assert body["role"] == "FARMER"
    assert "password_hash" not in body


def test_me_fails_without_jwt(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_fails_with_invalid_jwt(client):
    response = client.get(
        "/api/auth/me", headers=auth_headers("definitely.not.a.valid-token")
    )
    assert response.status_code == 401


def test_me_fails_with_expired_jwt(client):
    register_user(client)
    user = get_user_from_db("farmer@example.com")
    assert user is not None

    expired_token = create_access_token(
        subject=str(user.id), role=user.role, expires_delta=timedelta(minutes=-1)
    )
    response = client.get("/api/auth/me", headers=auth_headers(expired_token))
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# RBAC (temporary test endpoints)
# ---------------------------------------------------------------------------


def test_farmer_can_access_farmer_endpoint(client):
    register_user(client)
    token = obtain_token(client)

    response = client.get("/api/auth/test-farmer", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "FARMER access granted"


def test_consumer_cannot_access_farmer_endpoint(client):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    token = obtain_token(client, email="consumer@example.com")

    response = client.get("/api/auth/test-farmer", headers=auth_headers(token))
    assert response.status_code == 403


def test_admin_can_access_admin_endpoint(client):
    register_user(client, email="admin@example.com", role="ADMIN")
    token = obtain_token(client, email="admin@example.com")

    response = client.get("/api/auth/test-admin", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "ADMIN access granted"


def test_farmer_cannot_access_admin_endpoint(client):
    register_user(client)
    token = obtain_token(client)

    response = client.get("/api/auth/test-admin", headers=auth_headers(token))
    assert response.status_code == 403
