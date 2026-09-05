"""Tests for the Admin Verification module.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_admin(client: TestClient) -> str:
    """Register an admin user and return their JWT token."""
    register_user(client, email="admin@example.com", role="ADMIN")
    return obtain_token(client, email="admin@example.com")


def register_farmer_with_docs(client: TestClient, *, num_docs: int = 2) -> str:
    """Register a farmer, submit ``num_docs`` verification documents, return JWT."""
    register_user(client, email="farmer@example.com", role="FARMER")
    token = obtain_token(client, email="farmer@example.com")

    doc_types = ["AADHAAR", "PAN", "LAND_RECORD", "BANK_STATEMENT"]
    for i in range(num_docs):
        resp = client.post(
            "/api/verification/documents",
            headers=auth_headers(token),
            json={
                "document_type": doc_types[i % len(doc_types)],
                "document_number": f"DOC-{i:04d}",
            },
        )
        assert resp.status_code == 201, resp.text

    return token


# ---------------------------------------------------------------------------
# Verification queue
# ---------------------------------------------------------------------------


def test_admin_views_verification_queue(client):
    admin_token = register_admin(client)
    register_farmer_with_docs(client)

    response = client.get(
        "/api/admin/verifications", headers=auth_headers(admin_token)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body) >= 1
    item = body[0]
    assert item["farmer_email"] == "farmer@example.com"
    assert item["overall_status"] == "PENDING"
    assert item["document_count"] >= 1
    assert "earliest_submission" in item


def test_admin_views_verification_details(client):
    admin_token = register_admin(client)
    register_farmer_with_docs(client)

    # Find the farmer's user_id
    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    response = client.get(
        f"/api/admin/verifications/{farmer_id}", headers=auth_headers(admin_token)
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user_id"] == farmer_id
    assert body["farmer_name"] == "Test Farmer"
    assert body["farmer_email"] == "farmer@example.com"
    assert body["overall_status"] == "PENDING"
    assert len(body["documents"]) >= 1
    # Documents should have all expected fields
    doc = body["documents"][0]
    assert doc["status"] == "PENDING"
    assert "reviewed_by" in doc
    assert "reviewed_at" in doc


# ---------------------------------------------------------------------------
# Approve
# ---------------------------------------------------------------------------


def test_admin_approves_farmer(client):
    admin_token = register_admin(client)
    register_farmer_with_docs(client)

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
        admin = db.scalar(select(User).where(User.email == "admin@example.com"))
        admin_id = admin.id
    finally:
        db.close()

    response = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["action"] == "APPROVE"
    assert body["new_status"] == "APPROVED"
    assert body["reviewed_by"] == admin_id
    assert body["documents_updated"] >= 1
    assert "reviewed_at" in body

    # Verify documents are actually APPROVED in DB
    db = SessionLocal()
    try:
        from app.models.farmer import VerificationDocument

        docs = db.scalars(
            select(VerificationDocument).where(VerificationDocument.user_id == farmer_id)
        ).all()
        assert all(d.status == "APPROVED" for d in docs)
        assert all(d.reviewed_by == admin_id for d in docs)
        assert all(d.reviewed_at is not None for d in docs)
    finally:
        db.close()


def test_approved_farmer_visible_through_farmer_status(client):
    admin_token = register_admin(client)
    farmer_token = register_farmer_with_docs(client)

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    # Admin approves
    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200

    # Farmer sees APPROVED status
    resp = client.get(
        "/api/verification/status", headers=auth_headers(farmer_token)
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["overall_status"] == "APPROVED"
    assert all(d["status"] == "APPROVED" for d in body["documents"])


# ---------------------------------------------------------------------------
# Reject
# ---------------------------------------------------------------------------


def test_admin_rejects_farmer(client):
    admin_token = register_admin(client)
    register_farmer_with_docs(client)

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
        admin = db.scalar(select(User).where(User.email == "admin@example.com"))
        admin_id = admin.id
    finally:
        db.close()

    response = client.post(
        f"/api/admin/verifications/{farmer_id}/reject",
        headers=auth_headers(admin_token),
        json={"remarks": "Aadhaar number does not match records"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["action"] == "REJECT"
    assert body["new_status"] == "REJECTED"
    assert body["reviewed_by"] == admin_id
    assert body["remarks"] == "Aadhaar number does not match records"
    assert body["documents_updated"] >= 1

    # Verify documents are actually REJECTED in DB
    db = SessionLocal()
    try:
        from app.models.farmer import VerificationDocument

        docs = db.scalars(
            select(VerificationDocument).where(VerificationDocument.user_id == farmer_id)
        ).all()
        assert all(d.status == "REJECTED" for d in docs)
        assert all(d.remarks == "Aadhaar number does not match records" for d in docs)
        assert all(d.reviewed_by == admin_id for d in docs)
    finally:
        db.close()


def test_reject_requires_remarks(client):
    admin_token = register_admin(client)
    register_farmer_with_docs(client)

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    # Missing remarks → 422
    response = client.post(
        f"/api/admin/verifications/{farmer_id}/reject",
        headers=auth_headers(admin_token),
        json={},
    )
    assert response.status_code == 422


def test_rejected_farmer_visible_through_farmer_status(client):
    admin_token = register_admin(client)
    farmer_token = register_farmer_with_docs(client)

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "farmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    # Admin rejects
    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/reject",
        headers=auth_headers(admin_token),
        json={"remarks": "Documents are fraudulent"},
    )
    assert resp.status_code == 200

    # Farmer sees REJECTED status
    resp = client.get(
        "/api/verification/status", headers=auth_headers(farmer_token)
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["overall_status"] == "REJECTED"
    assert all(d["status"] == "REJECTED" for d in body["documents"])


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------


def test_farmer_cannot_access_admin_endpoints(client):
    register_user(client, email="farmer@example.com", role="FARMER")
    farmer_token = obtain_token(client, email="farmer@example.com")

    endpoints = [
        ("GET", "/api/admin/verifications"),
        ("GET", "/api/admin/verifications/1"),
        ("POST", "/api/admin/verifications/1/approve"),
        ("POST", "/api/admin/verifications/1/reject"),
    ]

    for method, path in endpoints:
        kwargs = {"headers": auth_headers(farmer_token)}
        if method == "POST" and "reject" in path:
            kwargs["json"] = {"remarks": "test"}

        if method == "GET":
            resp = client.get(path, **kwargs)
        else:
            resp = client.post(path, **kwargs)

        assert resp.status_code == 403, f"{method} {path} should be 403, got {resp.status_code}"


def test_consumer_cannot_access_admin_endpoints(client):
    register_user(client, email="consumer@example.com", role="CONSUMER")
    consumer_token = obtain_token(client, email="consumer@example.com")

    endpoints = [
        ("GET", "/api/admin/verifications"),
        ("GET", "/api/admin/verifications/1"),
        ("POST", "/api/admin/verifications/1/approve"),
        ("POST", "/api/admin/verifications/1/reject"),
    ]

    for method, path in endpoints:
        kwargs = {"headers": auth_headers(consumer_token)}
        if method == "POST" and "reject" in path:
            kwargs["json"] = {"remarks": "test"}

        if method == "GET":
            resp = client.get(path, **kwargs)
        else:
            resp = client.post(path, **kwargs)

        assert resp.status_code == 403, f"{method} {path} should be 403, got {resp.status_code}"


def test_unauthenticated_gets_401(client):
    endpoints = [
        ("GET", "/api/admin/verifications"),
        ("GET", "/api/admin/verifications/1"),
        ("POST", "/api/admin/verifications/1/approve"),
        ("POST", "/api/admin/verifications/1/reject"),
    ]

    for method, path in endpoints:
        kwargs = {}
        if method == "POST" and "reject" in path:
            kwargs["json"] = {"remarks": "test"}

        if method == "GET":
            resp = client.get(path, **kwargs)
        else:
            resp = client.post(path, **kwargs)

        assert resp.status_code == 401, f"{method} {path} should be 401, got {resp.status_code}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_nonexistent_farmer_returns_404(client):
    admin_token = register_admin(client)

    for path_suffix in ["/approve", "/reject"]:
        resp = client.post(
            f"/api/admin/verifications/99999{path_suffix}",
            headers=auth_headers(admin_token),
            **({"json": {"remarks": "test"}} if "reject" in path_suffix else {}),
        )
        assert resp.status_code == 404

    resp = client.get(
        "/api/admin/verifications/99999", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 404


def test_farmer_without_documents_returns_404(client):
    admin_token = register_admin(client)
    register_user(client, email="newfarmer@example.com", role="FARMER")

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "newfarmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    resp = client.get(
        f"/api/admin/verifications/{farmer_id}", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 404


def test_approve_farmer_without_documents_returns_404(client):
    admin_token = register_admin(client)
    register_user(client, email="newfarmer@example.com", role="FARMER")

    from sqlalchemy import select
    from app.core.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        farmer = db.scalar(select(User).where(User.email == "newfarmer@example.com"))
        farmer_id = farmer.id
    finally:
        db.close()

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404
