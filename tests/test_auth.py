"""Tests for the shared authentication + RBAC foundation.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)

These helpers centralize the role-specific identifiers so the whole suite
continues to work with the (new) contract:
- FARMER registers/logs in with a phone number (email stays optional).
- every other role registers/logs in with an email.
"""

import hashlib
import re
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# email -> role, tracked from register_user so login_user / obtain_token can
# pick the right identifier (phone for FARMER, email for others).
_REGISTERED_ROLES: dict[str, str] = {}


def derive_phone(email: str) -> str:
    """Deterministically derive a 10-digit phone number from an email string.

    Used so legacy test calls (which only pass an email) still produce a
    valid, stable phone for FARMER accounts. Always digits only.
    """
    base = re.sub(r"[^a-zA-Z0-9]", "", email or "").lower()
    digest = hashlib.md5(base.encode("utf-8")).digest()
    number = int.from_bytes(digest[:8], "big") % 10**9
    return f"9{number:09d}"


def register_user(
    client: TestClient,
    *,
    email: str = "farmer@example.com",
    phone: str | None = None,
    password: str = "password123",
    name: str = "Test Farmer",
    role: str = "FARMER",
):
    payload: dict[str, str] = {"name": name, "password": password, "role": role}
    if role == "FARMER":
        # FARMER authenticates by phone; keep email optional for backward
        # compatibility with the many tests that still register farmers with one.
        payload["phone"] = phone if phone is not None else derive_phone(email)
        payload["email"] = email
    else:
        payload["email"] = email

    resp = client.post("/api/auth/register", json=payload)
    if resp.status_code == 201:
        _REGISTERED_ROLES[email] = role
    return resp


def _resolve_identifier(email: str, phone: str | None) -> str:
    """Return the login identifier for a user registered with ``email``."""
    if phone is not None:
        return phone
    role = _REGISTERED_ROLES.get(email, "FARMER")
    if role == "FARMER":
        return derive_phone(email)
    return email


def login_user(
    client: TestClient,
    *,
    email: str = "farmer@example.com",
    phone: str | None = None,
    password: str = "password123",
):
    identifier = _resolve_identifier(email, phone)
    return client.post(
        "/api/auth/login", json={"identifier": identifier, "password": password}
    )


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def obtain_token(
    client: TestClient,
    *,
    email: str = "farmer@example.com",
    phone: str | None = None,
    password: str = "password123",
) -> str:
    """Register (if needed via caller) then login and return the JWT."""
    response = login_user(client, email=email, phone=phone, password=password)
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def get_user_from_db(email: str) -> User | None:
    db = SessionLocal()
    try:
        return db.scalar(select(User).where(User.email == email))
    finally:
        db.close()


def get_user_from_phone(phone: str) -> User | None:
    db = SessionLocal()
    try:
        return db.scalar(select(User).where(User.phone == phone))
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


# ---------------------------------------------------------------------------
# FARMER -> phone-based identifiers
# ---------------------------------------------------------------------------


def test_farmer_registration_with_phone_succeeds(client):
    """FARMER registers with a phone number (email not required)."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Ravi Kumar", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["phone"] == "9876543210"
    assert body["email"] is None
    assert body["role"] == "FARMER"
    assert "password_hash" not in body


def test_farmer_registration_without_phone_fails(client):
    """FARMER registration without a phone number returns 422."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Ravi Kumar", "password": "password123", "role": "FARMER"},
    )
    assert resp.status_code == 422


def test_farmer_registration_normalizes_phone(client):
    """Phone is normalized to a plain 10-digit number."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "+91 98765 43210", "password": "password123", "role": "FARMER"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["phone"] == "9876543210"


@pytest.mark.parametrize(
    "phone",
    ["12345", "abcdefghij", "98765432109", "0123456789", ""],
)
def test_farmer_registration_rejects_invalid_phone(client, phone):
    """Short, non-numeric, too-long, and leading-zero phones are rejected."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": phone, "password": "password123", "role": "FARMER"},
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]  # 422 body should not be empty


def test_duplicate_farmer_phone_rejected(client):
    """A second farmer with the same phone gets 409."""
    payload = {"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    dup = client.post("/api/auth/register", json={**payload, "name": "Another Farmer"})
    assert dup.status_code == 409
    assert "registered" in dup.json()["detail"].lower()


def test_farmer_login_with_phone_succeeds(client):
    """FARMER logs in using a phone number as the identifier."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"identifier": "9876543210", "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["phone"] == "9876543210"
    assert body["user"]["role"] == "FARMER"
    assert "password_hash" not in body["user"]


def test_farmer_login_accepts_formatted_phone(client):
    """A formatted phone number also resolves at login."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"identifier": "+91 98765 43210", "password": "password123"},
    )
    assert resp.status_code == 200, resp.text


def test_farmer_login_with_wrong_password_fails(client):
    """Wrong password returns a generic 401."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"identifier": "9876543210", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_farmer_login_with_invalid_phone_fails(client):
    """Unregistered or malformed phone identifiers return a generic 401."""
    unknown = client.post(
        "/api/auth/login",
        json={"identifier": "9999999999", "password": "password123"},
    )
    assert unknown.status_code == 401

    malformed = client.post(
        "/api/auth/login",
        json={"identifier": "123", "password": "password123"},
    )
    assert malformed.status_code == 401

    # Both produce the same generic message (no identifier enumeration).
    assert unknown.json()["detail"] == malformed.json()["detail"]


def test_farmer_can_call_me_with_phone_account(client):
    """A FARMER authenticated with a phone can call /api/auth/me."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    token = obtain_token(client, phone="9876543210")
    resp = client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "FARMER"
    assert "password_hash" not in resp.json()


def test_farmer_me_returns_phone(client):
    """/api/auth/me returns the farmer's phone number."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    token = obtain_token(client, phone="9876543210")
    resp = client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["phone"] == "9876543210"


def test_farmer_email_can_be_null(client):
    """A farmer registered with phone only has a null email on /me."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    token = obtain_token(client, phone="9876543210")
    resp = client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["email"] is None


# ---------------------------------------------------------------------------
# CONSUMER -> email-based identifiers
# ---------------------------------------------------------------------------


def test_consumer_registration_with_email_succeeds(client):
    """CONSUMER registers with an email address."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Arun Kumar", "email": "arun@example.com", "password": "password123", "role": "CONSUMER"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "arun@example.com"
    assert body["phone"] is None
    assert body["role"] == "CONSUMER"


def test_consumer_registration_without_email_fails(client):
    """CONSUMER registration without an email returns 422."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Arun", "password": "password123", "role": "CONSUMER"},
    )
    assert resp.status_code == 422


def test_consumer_registration_with_phone_rejected(client):
    """Non-farmer roles cannot register with a phone number."""
    resp = client.post(
        "/api/auth/register",
        json={"name": "Arun", "email": "arun@example.com", "phone": "9876543210", "password": "password123", "role": "CONSUMER"},
    )
    assert resp.status_code == 422


def test_consumer_login_with_email_succeeds(client):
    """CONSUMER logs in using an email as the identifier."""
    client.post(
        "/api/auth/register",
        json={"name": "Arun", "email": "arun@example.com", "password": "password123", "role": "CONSUMER"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"identifier": "arun@example.com", "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user"]["role"] == "CONSUMER"
    assert resp.json()["user"]["email"] == "arun@example.com"


def test_duplicate_consumer_email_rejected(client):
    """A second consumer with the same email gets 409."""
    payload = {"name": "Arun", "email": "arun@example.com", "password": "password123", "role": "CONSUMER"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    dup = client.post("/api/auth/register", json={**payload, "name": "Another Arun"})
    assert dup.status_code == 409
    assert "registered" in dup.json()["detail"].lower()


# ---------------------------------------------------------------------------
# OTHER ROLES -> email-based identifiers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "role,email",
    [
        ("BULK_BUYER", "bulk@example.com"),
        ("FINANCIER", "fin@example.com"),
        ("LOGISTICS", "log@example.com"),
        ("ADMIN", "admin@example.com"),
    ],
)
def test_other_roles_register_and_login_with_email(client, role, email):
    """BULK_BUYER / FINANCIER / LOGISTICS / ADMIN register and login by email."""
    reg = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": email, "password": "password123", "role": role},
    )
    assert reg.status_code == 201, reg.text
    assert reg.json()["email"] == email

    resp = client.post(
        "/api/auth/login",
        json={"identifier": email, "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["user"]["role"] == role
    assert resp.json()["user"]["email"] == email


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------


def test_password_hash_never_appears_in_login_response(client):
    """Login response user object never contains the password hash."""
    client.post(
        "/api/auth/register",
        json={"name": "Ravi", "phone": "9876543210", "password": "password123", "role": "FARMER"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"identifier": "9876543210", "password": "password123"},
    )
    assert resp.status_code == 200
    assert "password_hash" not in resp.json()
    assert "password_hash" not in resp.json()["user"]


def test_email_identifier_is_normalized_at_login(client):
    """Email identifiers are normalized (trimmed + case-insensitive) at login."""
    client.post(
        "/api/auth/register",
        json={"name": "Arun", "email": "arun@example.com", "password": "password123", "role": "CONSUMER"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"identifier": "  ARUN@Example.COM  ", "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
