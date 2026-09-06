"""Tests for P2 Basic Monitoring.

Covers the admin-only application + database health endpoint.

Run from the backend/ directory:   pytest
(no PostgreSQL required - tests use a disposable SQLite database)
"""

from fastapi.testclient import TestClient

from tests.test_auth import auth_headers, obtain_token, register_user


def _register_with_role(client: TestClient, role: str, email: str) -> str:
    """Register a user of the given role and return their JWT token."""
    register_user(client, email=email, role=role)
    return obtain_token(client, email=email)


# ---------------------------------------------------------------------------
# HEALTH / MONITORING
# ---------------------------------------------------------------------------


def test_admin_can_query_monitoring(client: TestClient):
    """ADMIN can access the monitoring endpoint and gets 200."""
    token = _register_with_role(client, "ADMIN", "admin_mon@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 200


def test_monitoring_response_structure(client: TestClient):
    """Monitoring response contains the expected basic fields."""
    token = _register_with_role(client, "ADMIN", "admin_struct@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()

    assert "application" in body
    assert "version" in body
    assert "status" in body
    assert "timestamp" in body
    assert "database" in body

    assert body["application"] == "SIH26033 Backend"
    assert isinstance(body["version"], str) and body["version"]
    assert body["status"] in {"ok", "degraded"}


def test_monitoring_database_connectivity_report(client: TestClient):
    """Monitoring reports database connectivity status."""
    token = _register_with_role(client, "ADMIN", "admin_db@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 200
    db_status = resp.json()["database"]

    # Database is up (disposable SQLite), so it must be reported as connected.
    assert db_status["status"] == "connected"
    assert db_status["error"] is False


def test_monitoring_timestamp_is_iso(client: TestClient):
    """Timestamp is an ISO-8601 datetime string."""
    token = _register_with_role(client, "ADMIN", "admin_ts@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 200
    ts = resp.json()["timestamp"]
    from datetime import datetime, timezone

    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None


# ---------------------------------------------------------------------------
# AUTHORIZATION
# ---------------------------------------------------------------------------


def test_unauthenticated_cannot_query_monitoring(client: TestClient):
    """Unauthenticated request to monitoring returns 401."""
    resp = client.get("/api/admin/monitoring")
    assert resp.status_code == 401


def test_consumer_cannot_query_monitoring(client: TestClient):
    """CONSUMER gets 403 on monitoring."""
    token = _register_with_role(client, "CONSUMER", "consumer_mon@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 403


def test_farmer_cannot_query_monitoring(client: TestClient):
    """FARMER gets 403 on monitoring."""
    token = _register_with_role(client, "FARMER", "farmer_mon@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 403


def test_bulk_buyer_cannot_query_monitoring(client: TestClient):
    """BULK_BUYER gets 403 on monitoring."""
    token = _register_with_role(client, "BULK_BUYER", "bulk_mon@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 403


def test_financier_cannot_query_monitoring(client: TestClient):
    """FINANCIER gets 403 on monitoring."""
    token = _register_with_role(client, "FINANCIER", "fin_mon@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 403


def test_logistics_cannot_query_monitoring(client: TestClient):
    """LOGISTICS gets 403 on monitoring."""
    token = _register_with_role(client, "LOGISTICS", "log_mon@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------


def test_monitoring_does_not_expose_secrets(client: TestClient):
    """Monitoring response does not leak DB credentials, JWT secrets, or tokens."""
    token = _register_with_role(client, "ADMIN", "admin_sec@example.com")
    resp = client.get("/api/admin/monitoring", headers=auth_headers(token))
    assert resp.status_code == 200

    raw = resp.text.lower()
    forbidden = {
        "password",
        "secret",
        "jwt",
        "token",
        "authorization",
        "sqlite",
        "postgres",
        "dsn",
        "connection string",
        "database url",
        "host",
        "port",
        "user",  # ensure no endpoint/account/user info
    }
    for term in forbidden:
        assert term not in raw, f"Potential secret leak: '{term}' found in monitoring response"

    # Auth header not reflected back
    assert "bearer" not in raw

    body = resp.json()
    # Explicitly confirm the documented safe keyset only
    assert set(body.keys()) == {
        "application",
        "version",
        "status",
        "timestamp",
        "database",
    }
    assert set(body["database"].keys()) == {"status", "error"}
