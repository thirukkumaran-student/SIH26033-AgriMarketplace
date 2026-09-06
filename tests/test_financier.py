"""Tests for the Financier module.

Covers:
- Financier profile CRUD
- Financier verification
- Admin approval/rejection
- Verified financier discovery by BULK_BUYER
"""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.user import User
from tests.test_auth import auth_headers, obtain_token, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_financier(
    client: TestClient,
    email: str = "financier@example.com",
) -> str:
    """Register a financier and return their JWT token."""
    register_user(
        client,
        email=email,
        name="Test Financier",
        role="FINANCIER",
    )
    return obtain_token(client, email=email)


def create_financier_profile(
    client: TestClient,
    token: str,
    institution_name: str = "Test Finance Ltd",
) -> dict:
    """Create a financier profile and return the response body."""
    response = client.post(
        "/api/financier/profile",
        headers=auth_headers(token),
        json={
            "institution_name": institution_name,
            "institution_type": "NBFC",
            "phone": "9876543210",
            "address": "Finance Street",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def submit_financier_document(
    client: TestClient,
    token: str,
    document_number: str = "FIN-DOC-001",
) -> dict:
    """Submit one verification document for a financier."""
    response = client.post(
        "/api/verification/documents",
        headers=auth_headers(token),
        json={
            "document_type": "REGISTRATION_CERTIFICATE",
            "document_number": document_number,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def get_user_id(email: str) -> int:
    """Get a user's database ID."""
    db = SessionLocal()
    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )
        assert user is not None
        return user.id
    finally:
        db.close()


def register_admin(client: TestClient) -> str:
    """Register an admin and return their JWT token."""
    register_user(
        client,
        email="admin_financier@example.com",
        role="ADMIN",
    )
    return obtain_token(
        client,
        email="admin_financier@example.com",
    )


def approve_financier(
    client: TestClient,
    financier_token: str,
    financier_email: str = "financier@example.com",
) -> str:
    """Submit verification and approve the financier."""
    submit_financier_document(client, financier_token)

    admin_token = register_admin(client)
    financier_id = get_user_id(financier_email)

    response = client.post(
        f"/api/admin/verifications/{financier_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text

    return admin_token


# ---------------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------------


def test_financier_can_create_profile(client: TestClient):
    token = register_financier(client)

    body = create_financier_profile(client, token)

    assert body["institution_name"] == "Test Finance Ltd"
    assert body["institution_type"] == "NBFC"


def test_financier_can_get_own_profile(client: TestClient):
    token = register_financier(client)
    create_financier_profile(client, token)

    response = client.get(
        "/api/financier/profile",
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["institution_name"] == "Test Finance Ltd"


def test_financier_can_update_profile(client: TestClient):
    token = register_financier(client)
    create_financier_profile(client, token)

    response = client.put(
        "/api/financier/profile",
        headers=auth_headers(token),
        json={
            "institution_name": "Updated Finance Ltd",
            "city": "Bengaluru",
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["institution_name"] == "Updated Finance Ltd"
    assert body["city"] == "Bengaluru"


def test_financier_cannot_create_duplicate_profile(client: TestClient):
    token = register_financier(client)

    create_financier_profile(client, token)

    response = client.post(
        "/api/financier/profile",
        headers=auth_headers(token),
        json={"institution_name": "Another Finance"},
    )

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# VERIFICATION
# ---------------------------------------------------------------------------


def test_financier_can_submit_verification_document(client: TestClient):
    token = register_financier(client)

    body = submit_financier_document(client, token)

    assert body["document_type"] == "REGISTRATION_CERTIFICATE"
    assert body["status"] == "PENDING"


def test_financier_can_view_verification_status(client: TestClient):
    token = register_financier(client)

    submit_financier_document(client, token)

    response = client.get(
        "/api/verification/status",
        headers=auth_headers(token),
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["user_id"] == get_user_id("financier@example.com")
    assert body["overall_status"] == "PENDING"
    assert len(body["documents"]) == 1


def test_admin_can_approve_financier(client: TestClient):
    token = register_financier(client)
    admin_token = approve_financier(client, token)

    financier_id = get_user_id("financier@example.com")

    response = client.get(
        f"/api/admin/verifications/{financier_id}",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["overall_status"] == "APPROVED"


# ---------------------------------------------------------------------------
# DISCOVERY
# ---------------------------------------------------------------------------


def test_bulk_buyer_can_discover_approved_financier(client: TestClient):
    financier_token = register_financier(client)
    create_financier_profile(client, financier_token)

    approve_financier(client, financier_token)

    register_user(
        client,
        email="bulk_discovery@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="bulk_discovery@example.com",
    )

    response = client.get(
        "/api/financier/",
        headers=auth_headers(buyer_token),
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert len(body) == 1
    assert body[0]["institution_name"] == "Test Finance Ltd"


def test_pending_financier_is_not_discoverable(client: TestClient):
    financier_token = register_financier(client)
    create_financier_profile(client, financier_token)

    submit_financier_document(client, financier_token)

    register_user(
        client,
        email="bulk_pending@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="bulk_pending@example.com",
    )

    response = client.get(
        "/api/financier/",
        headers=auth_headers(buyer_token),
    )

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_financier_without_documents_is_not_discoverable(client: TestClient):
    financier_token = register_financier(client)
    create_financier_profile(client, financier_token)

    register_user(
        client,
        email="bulk_no_docs@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="bulk_no_docs@example.com",
    )

    response = client.get(
        "/api/financier/",
        headers=auth_headers(buyer_token),
    )

    assert response.status_code == 200, response.text
    assert response.json() == []


# ---------------------------------------------------------------------------
# DISCOVERY RBAC
# ---------------------------------------------------------------------------


def test_consumer_cannot_discover_financiers(client: TestClient):
    register_user(
        client,
        email="consumer_financier@example.com",
        role="CONSUMER",
    )
    token = obtain_token(
        client,
        email="consumer_financier@example.com",
    )

    response = client.get(
        "/api/financier/",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_farmer_cannot_discover_financiers(client: TestClient):
    register_user(
        client,
        email="farmer_financier@example.com",
        role="FARMER",
    )
    token = obtain_token(
        client,
        email="farmer_financier@example.com",
    )

    response = client.get(
        "/api/financier/",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_financier_cannot_discover_financiers(client: TestClient):
    token = register_financier(client)

    response = client.get(
        "/api/financier/",
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_unauthenticated_cannot_discover_financiers(client: TestClient):
    response = client.get("/api/financier/")

    assert response.status_code == 401