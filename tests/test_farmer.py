"""Tests for the Farmer Profile and Farmer Verification modules.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers (reuse test_auth helpers where possible)
# ---------------------------------------------------------------------------

from tests.test_auth import auth_headers, register_user, obtain_token


def create_profile(client: TestClient, token: str, **overrides) -> dict:
    """Create a farmer profile and return the response body."""
    payload = {
        "phone": "9876543210",
        "farm_name": "Green Acres",
        "farm_size_acres": 15.0,
        "farm_location": "Village Rampur, District Meerut, UP",
        "soil_type": "Loam",
        "irrigation_type": "Drip",
        "bank_account_number": "1234567890",
        "ifsc_code": "SBIN0001234",
    }
    payload.update(overrides)
    response = client.post(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json=payload,
    )
    return response.json() if response.status_code in (200, 201) else response.json()


def submit_document(
    client: TestClient,
    token: str,
    *,
    document_type: str = "AADHAAR",
    document_number: str = "1234-5678-9012",
    file_url: str | None = None,
) -> dict:
    """Submit a verification document."""
    payload = {"document_type": document_type, "document_number": document_number}
    if file_url is not None:
        payload["file_url"] = file_url
    response = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json=payload,
    )
    return response.json() if response.status_code in (200, 201) else response.json()


# ---------------------------------------------------------------------------
# Farmer Profile
# ---------------------------------------------------------------------------


def test_farmer_creates_profile(client):
    register_user(client)
    token = obtain_token(client)

    response = client.post(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={
            "phone": "9876543210",
            "farm_name": "Green Acres",
            "farm_size_acres": 15.0,
            "farm_location": "Village Rampur",
            "soil_type": "Loam",
            "irrigation_type": "Drip",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["farm_name"] == "Green Acres"
    assert body["phone"] == "9876543210"
    assert body["farm_size_acres"] == 15.0
    assert body["user_id"] > 0
    assert "created_at" in body
    assert "updated_at" in body


def test_farmer_cannot_create_duplicate_profile(client):
    register_user(client)
    token = obtain_token(client)

    first = client.post(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={"phone": "9876543210", "farm_name": "First"},
    )
    assert first.status_code == 201, first.text

    second = client.post(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={"phone": "1111111111", "farm_name": "Second"},
    )
    assert second.status_code == 409
    assert "already exists" in second.json()["detail"].lower()


def test_farmer_reads_own_profile(client):
    register_user(client)
    token = obtain_token(client)
    create_profile(client, token)

    response = client.get("/api/farmer/profile", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    assert response.json()["farm_name"] == "Green Acres"


def test_farmer_profile_not_found(client):
    register_user(client)
    token = obtain_token(client)

    response = client.get("/api/farmer/profile", headers=auth_headers(token))
    assert response.status_code == 404


def test_farmer_updates_own_profile(client):
    register_user(client)
    token = obtain_token(client)
    create_profile(client, token)

    response = client.put(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={"farm_name": "Green Acres Updated", "farm_size_acres": 20.0},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["farm_name"] == "Green Acres Updated"
    assert body["farm_size_acres"] == 20.0
    # Unchanged fields remain
    assert body["phone"] == "9876543210"


def test_farmer_update_profile_not_found(client):
    register_user(client)
    token = obtain_token(client)

    response = client.put(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={"farm_name": "No Profile"},
    )
    assert response.status_code == 404


def test_non_farmer_cannot_access_profile(client):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    token = obtain_token(client, email="consumer@example.com")

    # GET
    resp = client.get("/api/farmer/profile", headers=auth_headers(token))
    assert resp.status_code == 403

    # POST
    resp = client.post(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={"phone": "000"},
    )
    assert resp.status_code == 403

    # PUT
    resp = client.put(
        "/api/farmer/profile",
        headers=auth_headers(token),
        json={"phone": "000"},
    )
    assert resp.status_code == 403


def test_unauthenticated_cannot_access_profile(client):
    response = client.get("/api/farmer/profile")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Verification Documents
# ---------------------------------------------------------------------------


def test_farmer_submits_verification_document(client):
    register_user(client)
    token = obtain_token(client)

    response = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={
            "document_type": "AADHAAR",
            "document_number": "1234-5678-9012",
            "file_url": "https://example.com/aadhaar.pdf",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["document_type"] == "AADHAAR"
    assert body["document_number"] == "1234-5678-9012"
    assert body["status"] == "PENDING"
    assert body["user_id"] > 0
    assert body["remarks"] is None


def test_farmer_submits_multiple_documents(client):
    register_user(client)
    token = obtain_token(client)

    r1 = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "1111"},
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "PAN", "document_number": "ABCDE1234F"},
    )
    assert r2.status_code == 201


def test_farmer_views_verification_status(client):
    register_user(client)
    token = obtain_token(client)
    submit_document(client, token, document_type="AADHAAR", document_number="1111")
    submit_document(client, token, document_type="PAN", document_number="ABCDE1234F")

    response = client.get("/api/verification/status", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user_id"] > 0
    assert body["farmer_name"] == "Test Farmer"
    assert len(body["documents"]) == 2
    assert body["overall_status"] == "PENDING"  # at least one PENDING


def test_verification_status_not_found(client):
    register_user(client)
    token = obtain_token(client)

    response = client.get("/api/verification/status", headers=auth_headers(token))
    assert response.status_code == 404


def test_non_farmer_cannot_submit_document(client):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    token = obtain_token(client, email="consumer@example.com")

    response = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={"document_type": "AADHAAR", "document_number": "1234"},
    )
    assert response.status_code == 403


def test_non_farmer_cannot_view_verification_status(client):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    token = obtain_token(client, email="consumer@example.com")

    response = client.get("/api/verification/status", headers=auth_headers(token))
    assert response.status_code == 403


def test_unauthenticated_cannot_submit_document(client):
    response = client.post(
        "/api/verification/documents",
        json={"document_type": "AADHAAR", "document_number": "1234"},
    )
    assert response.status_code == 401


def test_unauthenticated_cannot_view_verification_status(client):
    response = client.get("/api/verification/status")
    assert response.status_code == 401


def test_verification_status_all_approved(client):
    """When all documents are approved (set directly in DB for test), overall = APPROVED."""
    register_user(client)
    token = obtain_token(client)
    submit_document(client, token, document_type="AADHAAR", document_number="1111")

    # Simulate admin approval by updating the record directly
    from sqlalchemy import select

    from app.core.database import SessionLocal
    from app.models.farmer import VerificationDocument
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == "farmer@example.com"))
        assert user is not None, "User not found in test DB"
        doc = db.scalar(
            select(VerificationDocument).where(VerificationDocument.user_id == user.id)
        )
        assert doc is not None, "VerificationDocument not found in test DB"
        doc.status = "APPROVED"
        db.commit()
        db.expire_all()  # clear the identity map so the next read is fresh
    finally:
        db.close()

    response = client.get("/api/verification/status", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    assert response.json()["overall_status"] == "APPROVED"
