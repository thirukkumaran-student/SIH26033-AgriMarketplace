"""Tests for P2 Admin Disputes and Dispute Resolution.

Covers consumer dispute creation and admin dispute management.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user
from tests.test_consumer import register_consumer
from tests.test_orders import create_produce


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _place_order_and_confirm(client: TestClient, quantity: int = 5) -> tuple[str, dict, str]:
    """Register farmer, approve, create produce, place consumer order, confirm.
    Returns (farmer_token, order_body, consumer_token).
    """
    register_user(client, email="farmer_dispute@example.com", role="FARMER")
    farmer_token = obtain_token(client, email="farmer_dispute@example.com")

    for doc_type in ["AADHAAR", "PAN"]:
        resp = client.post(
            "/api/verification/documents",
            headers=auth_headers(farmer_token),
            json={"document_type": doc_type, "document_number": f"DOC-{doc_type}"},
        )
        assert resp.status_code == 201, resp.text

    register_user(client, email="admin_dispute@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_dispute@example.com")

    from app.core.security import decode_access_token
    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200, resp.text

    body = create_produce(client, farmer_token, crop="Dispute Wheat", quantity=100, price_per_unit=25.0)

    register_user(client, email="consumer_dispute@example.com", name="Consumer Dispute", role="CONSUMER")
    consumer_token = obtain_token(client, email="consumer_dispute@example.com")

    order_resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": body["id"], "quantity": quantity},
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()

    # Farmer confirms the order
    client.patch(
        f"/api/orders/{order['id']}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )

    return farmer_token, order, consumer_token


def _create_dispute(client: TestClient, consumer_token: str, order_id: int, reason: str = "Quality issue") -> dict:
    """Helper to create a dispute."""
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order_id, "reason": reason, "description": "Product was damaged"},
    )
    return resp.json() if resp.status_code in (200, 201) else None


# ---------------------------------------------------------------------------
# CONSUMER DISPUTE CREATION — AUTHENTICATION
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_create_dispute(client: TestClient):
    """Unauthenticated request returns 401."""
    resp = client.post(
        "/api/consumer/disputes",
        json={"order_id": 1, "reason": "Quality issue"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# CONSUMER DISPUTE CREATION — AUTHORIZATION
# ---------------------------------------------------------------------------


def test_consumer_can_create_dispute(client: TestClient):
    """CONSUMER can create a dispute on their own order."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order["id"], "reason": "Quality issue"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["order_id"] == order["id"]
    assert body["reason"] == "Quality issue"
    assert body["status"] == "OPEN"
    assert body["raised_by"] > 0


def test_farmer_cannot_create_dispute(client: TestClient):
    """FARMER gets 403 on dispute creation."""
    farmer_token, order, _ = _place_order_and_confirm(client)

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(farmer_token),
        json={"order_id": order["id"], "reason": "Quality issue"},
    )
    assert resp.status_code == 403


def test_bulk_buyer_cannot_create_dispute(client: TestClient):
    """BULK_BUYER gets 403."""
    register_user(client, email="bulk_dispute@example.com", role="BULK_BUYER")
    token = obtain_token(client, email="bulk_dispute@example.com")

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(token),
        json={"order_id": 1, "reason": "Quality issue"},
    )
    assert resp.status_code == 403


def test_financier_cannot_create_dispute(client: TestClient):
    """FINANCIER gets 403."""
    register_user(client, email="fin_dispute@example.com", role="FINANCIER")
    token = obtain_token(client, email="fin_dispute@example.com")
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(token),
        json={"order_id": 1, "reason": "Quality issue"},
    )
    assert resp.status_code == 403


def test_logistics_cannot_create_dispute(client: TestClient):
    """LOGISTICS gets 403."""
    register_user(client, email="log_dispute@example.com", role="LOGISTICS")
    token = obtain_token(client, email="log_dispute@example.com")
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(token),
        json={"order_id": 1, "reason": "Quality issue"},
    )
    assert resp.status_code == 403


def test_admin_cannot_create_dispute(client: TestClient):
    """ADMIN gets 403."""
    register_user(client, email="admin_dispute_create@example.com", role="ADMIN")
    token = obtain_token(client, email="admin_dispute_create@example.com")
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(token),
        json={"order_id": 1, "reason": "Quality issue"},
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# CONSUMER DISPUTE CREATION — OWNERSHIP & VALIDATION
# ---------------------------------------------------------------------------


def test_consumer_can_only_dispute_own_order(client: TestClient):
    """Consumer cannot dispute another consumer's order."""
    farmer_token, order, _ = _place_order_and_confirm(client)

    # Register another consumer
    register_user(client, email="consumer_other@example.com", name="Consumer Other", role="CONSUMER")
    other_token = obtain_token(client, email="consumer_other@example.com")

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(other_token),
        json={"order_id": order["id"], "reason": "Quality issue"},
    )
    assert resp.status_code == 403


def test_nonexistent_order_returns_404(client: TestClient):
    """Nonexistent order returns 404."""
    register_user(client, email="consumer_nonexist@example.com", name="Consumer Nonexist", role="CONSUMER")
    token = obtain_token(client, email="consumer_nonexist@example.com")

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(token),
        json={"order_id": 99999, "reason": "Quality issue"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_cancelled_order_cannot_be_disputed(client: TestClient):
    """Cancelled orders cannot be disputed."""
    # Register farmer, approve, create produce
    register_user(client, email="farmer_cancel@example.com", role="FARMER")
    farmer_token = obtain_token(client, email="farmer_cancel@example.com")

    for doc_type in ["AADHAAR", "PAN"]:
        resp = client.post(
            "/api/verification/documents",
            headers=auth_headers(farmer_token),
            json={"document_type": doc_type, "document_number": f"DOC-{doc_type}"},
        )
        assert resp.status_code == 201, resp.text

    register_user(client, email="admin_cancel@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_cancel@example.com")

    from app.core.security import decode_access_token
    payload = decode_access_token(farmer_token)
    farmer_id = int(payload["sub"])

    resp = client.post(
        f"/api/admin/verifications/{farmer_id}/approve",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200, resp.text

    from tests.test_orders import create_produce as _cp
    body = _cp(client, farmer_token, crop="Cancel Crop", quantity=100, price_per_unit=25.0)

    register_user(client, email="consumer_cancel@example.com", name="Consumer Cancel", role="CONSUMER")
    consumer_token = obtain_token(client, email="consumer_cancel@example.com")

    # Place order but DON'T confirm it — keep it PENDING so consumer can cancel
    order_resp = client.post(
        "/api/orders",
        headers=auth_headers(consumer_token),
        json={"produce_id": body["id"], "quantity": 5},
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()

    # Consumer cancels the PENDING order
    client.patch(
        f"/api/orders/{order['id']}/status",
        headers=auth_headers(consumer_token),
        json={"status": "CANCELLED"},
    )

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order["id"], "reason": "Quality issue"},
    )
    assert resp.status_code == 400
    assert "cancelled" in resp.json()["detail"].lower()


def test_duplicate_open_dispute_rejected(client: TestClient):
    """Only one open dispute per order is allowed."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)

    # First dispute
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order["id"], "reason": "Quality issue"},
    )
    assert resp.status_code == 201

    # Second dispute for same order
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order["id"], "reason": "Different issue"},
    )
    assert resp.status_code == 409
    assert "open dispute" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# ADMIN DISPUTE LIST
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_list_disputes(client: TestClient):
    """Unauthenticated request returns 401."""
    resp = client.get("/api/admin/disputes")
    assert resp.status_code == 401


def test_farmer_cannot_list_disputes(client: TestClient):
    """FARMER gets 403."""
    farmer_token, _, _ = _place_order_and_confirm(client)
    resp = client.get(
        "/api/admin/disputes",
        headers=auth_headers(farmer_token),
    )
    assert resp.status_code == 403


def test_bulk_buyer_cannot_list_disputes(client: TestClient):
    """BULK_BUYER gets 403."""
    register_user(client, email="bulk_dispute_list@example.com", role="BULK_BUYER")
    token = obtain_token(client, email="bulk_dispute_list@example.com")
    resp = client.get(
        "/api/admin/disputes",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_financier_cannot_list_disputes(client: TestClient):
    """FINANCIER gets 403."""
    register_user(client, email="fin_dispute_list@example.com", role="FINANCIER")
    token = obtain_token(client, email="fin_dispute_list@example.com")
    resp = client.get(
        "/api/admin/disputes",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_logistics_cannot_list_disputes(client: TestClient):
    """LOGISTICS gets 403."""
    register_user(client, email="log_dispute_list@example.com", role="LOGISTICS")
    token = obtain_token(client, email="log_dispute_list@example.com")
    resp = client.get(
        "/api/admin/disputes",
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_admin_can_list_disputes(client: TestClient):
    """ADMIN can list all disputes."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_dispute_list@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_dispute_list@example.com")

    resp = client.get(
        "/api/admin/disputes",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 1
    assert body[0]["order_id"] == order["id"]
    assert body[0]["status"] == "OPEN"


def test_admin_gets_empty_list(client: TestClient):
    """ADMIN gets empty list when no disputes exist."""
    register_user(client, email="admin_dispute_empty@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_dispute_empty@example.com")

    resp = client.get(
        "/api/admin/disputes",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# ADMIN DISPUTE DETAILS
# ---------------------------------------------------------------------------


def test_admin_can_get_dispute_detail(client: TestClient):
    """ADMIN can get dispute detail."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_dispute_detail@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_dispute_detail@example.com")

    resp = client.get(
        f"/api/admin/disputes/{dispute_body['id']}",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["order_id"] == order["id"]
    assert body["crop"] == "Dispute Wheat"
    assert body["reason"] == "Quality issue"
    assert body["status"] == "OPEN"


def test_nonexistent_dispute_returns_404(client: TestClient):
    """Nonexistent dispute returns 404."""
    register_user(client, email="admin_nonexist@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_nonexist@example.com")

    resp = client.get(
        "/api/admin/disputes/99999",
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404


def test_admin_detail_returns_order_information(client: TestClient):
    """Dispute detail includes order information like crop, quantity, total."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client, quantity=10)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_detail_order@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_detail_order@example.com")

    resp = client.get(
        f"/api/admin/disputes/{dispute_body['id']}",
        headers=auth_headers(admin_token),
    )
    body = resp.json()
    assert body["order_id"] == order["id"]
    assert body["order_quantity"] == 10
    assert body["order_total_amount"] == 250.0
    assert body["crop"] == "Dispute Wheat"
    assert body["order_status"] == "CONFIRMED"


def test_admin_detail_does_not_expose_sensitive_pii(client: TestClient):
    """Dispute detail does not expose sensitive PII."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_sensitive@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_sensitive@example.com")

    resp = client.get(
        f"/api/admin/disputes/{dispute_body['id']}",
        headers=auth_headers(admin_token),
    )
    body = resp.json()
    sensitive_keys = {"password", "password_hash", "email", "phone", "hashed_password", "documents", "aadhaar", "pan"}
    for key in sensitive_keys:
        assert key not in body, f"Sensitive key '{key}' exposed in dispute detail"


# ---------------------------------------------------------------------------
# DISPUTE RESOLUTION
# ---------------------------------------------------------------------------


def test_admin_can_resolve_dispute_accepted(client: TestClient):
    """ADMIN can resolve a dispute as ACCEPTED."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_resolve@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_resolve@example.com")

    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "ACCEPTED", "admin_remarks": "Refund issued"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ACCEPTED"
    assert body["resolution"] == "ACCEPTED"
    assert body["admin_remarks"] == "Refund issued"
    assert body["resolved_by"] > 0
    assert body["resolved_at"] is not None


def test_admin_can_resolve_dispute_rejected(client: TestClient):
    """ADMIN can resolve a dispute as REJECTED."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_reject_dispute@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_reject_dispute@example.com")

    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "REJECTED", "admin_remarks": "No evidence"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "REJECTED"


def test_admin_can_resolve_dispute_partial(client: TestClient):
    """ADMIN can resolve a dispute as PARTIAL."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_partial@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_partial@example.com")

    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "PARTIAL", "admin_remarks": "Partial refund"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "PARTIAL"


def test_invalid_resolution_rejected(client: TestClient):
    """Invalid resolution value is rejected."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_invalid@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_invalid@example.com")

    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "INVALID", "admin_remarks": "Test"},
    )
    assert resp.status_code == 422


def test_already_resolved_cannot_be_resolved_again(client: TestClient):
    """Already resolved dispute cannot be resolved again."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_already@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_already@example.com")

    # Resolve first time
    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "ACCEPTED"},
    )
    assert resp.status_code == 200

    # Try resolving again
    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "REJECTED"},
    )
    assert resp.status_code == 400
    assert "already resolved" in resp.json()["detail"].lower()


def test_non_admin_cannot_resolve_dispute(client: TestClient):
    """Non-admin cannot resolve disputes."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="farmer_resolve@example.com", role="FARMER")
    token = obtain_token(client, email="farmer_resolve@example.com")

    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(token),
        json={"resolution": "ACCEPTED"},
    )
    assert resp.status_code == 403


def test_resolved_by_cannot_be_overridden(client: TestClient):
    """Admin identity comes from JWT, client cannot override resolved_by."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_override@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_override@example.com")

    resp = client.post(
        f"/api/admin/disputes/{dispute_body['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "ACCEPTED", "admin_remarks": "Test"},
    )
    body = resp.json()
    # resolved_by should be the admin's user ID from JWT, not a client-supplied value
    from app.core.security import decode_access_token
    admin_id = int(decode_access_token(admin_token)["sub"])
    assert body["resolved_by"] == admin_id


# ---------------------------------------------------------------------------
# INTEGRATION TEST
# ---------------------------------------------------------------------------


def test_full_dispute_workflow(client: TestClient):
    """Full workflow: order → dispute → admin list → admin detail → resolve."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)

    # Consumer creates dispute
    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order["id"], "reason": "Quality issue", "description": "Damaged product"},
    )
    assert resp.status_code == 201
    dispute = resp.json()
    assert dispute["status"] == "OPEN"

    # Admin lists disputes
    register_user(client, email="admin_full@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_full@example.com")

    resp = client.get("/api/admin/disputes", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

    # Admin gets dispute detail
    resp = client.get(f"/api/admin/disputes/{dispute['id']}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["crop"] == "Dispute Wheat"
    assert resp.json()["order_status"] == "CONFIRMED"

    # Admin resolves as ACCEPTED
    resp = client.post(
        f"/api/admin/disputes/{dispute['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "ACCEPTED"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACCEPTED"
    assert resp.json()["resolution"] == "ACCEPTED"

    # Admin cannot resolve again
    resp = client.post(
        f"/api/admin/disputes/{dispute['id']}/resolve",
        headers=auth_headers(admin_token),
        json={"resolution": "REJECTED"},
    )
    assert resp.status_code == 400


def test_dispute_references_correct_order(client: TestClient):
    """Dispute references the correct order."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)
    dispute_body = _create_dispute(client, consumer_token, order["id"])

    register_user(client, email="admin_check@example.com", role="ADMIN")
    admin_token = obtain_token(client, email="admin_check@example.com")

    resp = client.get(f"/api/admin/disputes/{dispute_body['id']}", headers=auth_headers(admin_token))
    assert resp.json()["order_id"] == order["id"]


def test_consumer_returns_correct_dispute_response(client: TestClient):
    """Consumer dispute creation returns correct response fields."""
    farmer_token, order, consumer_token = _place_order_and_confirm(client)

    resp = client.post(
        "/api/consumer/disputes",
        headers=auth_headers(consumer_token),
        json={"order_id": order["id"], "reason": "Quality issue"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert "order_id" in body
    assert "raised_by" in body
    assert "reason" in body
    assert "status" in body
    assert body["status"] == "OPEN"
    assert "created_at" in body
    assert "updated_at" in body
    # Should not have resolution fields initially
    assert "resolution" not in body or body["resolution"] is None
    assert "admin_remarks" not in body or body["admin_remarks"] is None
