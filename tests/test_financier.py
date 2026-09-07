"""Tests for the Financier module.

Covers:
- Financier profile CRUD
- Financier verification
- Admin approval/rejection
- Verified financier discovery by BULK_BUYER
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import relationship

from app.core.database import SessionLocal
from app.models.user import User
from tests.test_auth import auth_headers, obtain_token, register_user
from decimal import Decimal

from app.models.buyer import BuyerProfile
from app.models.order import Order
from app.modules.finance.models import (
    FinancingRelationship,
    FinancingTransaction,
)

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

def create_financing_request(
    client: TestClient,
    buyer_token: str,
    financier_id: int,
) -> dict:
    """Create a financing request for a buyer."""
    response = client.post(
        "/api/finance/requests",
        headers=auth_headers(buyer_token),
        json={
            "financier_id": financier_id,
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


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
# FINANCING REQUESTS
# ---------------------------------------------------------------------------


def test_bulk_buyer_can_view_own_financing_requests(client: TestClient):
    financier_token = register_financier(
        client,
        email="request_financier@example.com",
    )

    financier_id = get_user_id("request_financier@example.com")

    register_user(
        client,
        email="request_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="request_buyer@example.com",
    )

    request_body = create_financing_request(
        client,
        buyer_token,
        financier_id,
    )

    assert request_body["buyer_id"] == get_user_id(
        "request_buyer@example.com"
    )
    assert request_body["financier_id"] == financier_id
    assert request_body["status"] == "PENDING"

    response = client.get(
        "/api/finance/requests",
        headers=auth_headers(buyer_token),
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == request_body["id"]
    assert body[0]["buyer_id"] == request_body["buyer_id"]
    assert body[0]["financier_id"] == financier_id
    assert body[0]["status"] == "PENDING"

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

def test_bulk_buyer_can_view_and_select_approved_financing_offer(
    client: TestClient,
):
    financier_token = register_financier(
        client,
        email="offer_financier@example.com",
    )

    financier_id = get_user_id("offer_financier@example.com")

    register_user(
        client,
        email="offer_buyer@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="offer_buyer@example.com",
    )

    request_body = create_financing_request(
        client,
        buyer_token,
        financier_id,
    )

    request_id = request_body["id"]

    # Financier approves the request.
    response = client.post(
        f"/api/finance/requests/{request_id}/approve",
        headers=auth_headers(financier_token),
        json={
            "credit_limit": 100000,
            "interest_rate": 10,
            "tenure_days": 90,
        },
    )

    assert response.status_code == 200, response.text

    approved_body = response.json()

    assert approved_body["status"] == "APPROVED"
    assert approved_body["credit_limit"] == "100000.00"
    assert approved_body["interest_rate"] == "10.00"
    assert approved_body["tenure_days"] == 90

    # Buyer can now see the approved offer.
    response = client.get(
        "/api/finance/requests",
        headers=auth_headers(buyer_token),
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == request_id
    assert body[0]["status"] == "APPROVED"
    assert body[0]["credit_limit"] == "100000.00"
    assert body[0]["interest_rate"] == "10.00"
    assert body[0]["tenure_days"] == 90

    # Buyer selects the offer.
    response = client.post(
        f"/api/finance/requests/{request_id}/select",
        headers=auth_headers(buyer_token),
    )

    assert response.status_code == 200, response.text

    relationship = response.json()

    assert relationship["buyer_id"] == get_user_id(
        "offer_buyer@example.com"
    )
    assert relationship["financier_id"] == financier_id
    assert relationship["credit_limit"] == "100000.00"
    assert relationship["interest_rate"] == "10.00"
    assert relationship["tenure_days"] == 90
    assert relationship["status"] == "ACTIVE"

def test_financier_can_view_only_requests_sent_to_them(
    client: TestClient,
):
    financier_token = register_financier(
        client,
        email="requests_owner@example.com",
    )

    financier_id = get_user_id("requests_owner@example.com")

    register_user(
        client,
        email="request_sender@example.com",
        role="BULK_BUYER",
    )
    buyer_token = obtain_token(
        client,
        email="request_sender@example.com",
    )

    create_financing_request(
        client,
        buyer_token,
        financier_id,
    )

    response = client.get(
        "/api/finance/requests",
        headers=auth_headers(financier_token),
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert len(body) == 1
    assert body[0]["financier_id"] == financier_id
    assert body[0]["buyer_id"] == get_user_id(
        "request_sender@example.com"
    )