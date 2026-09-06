"""Admin Monitoring Route.

- GET /api/admin/monitoring  -> basic application + database health

Only ADMIN can access this endpoint.

This provides BASIC monitoring only (no observability stack):
- application status
- database connectivity/status
- current timestamp / version

It fails gracefully if the database is unavailable: the endpoint still
returns 200 with ``database.status = "error"`` rather than leaking raw
exception details to the client.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.models.user import User
from app.modules.auth.dependencies import require_role
from app.schemas.admin import MonitoringResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])
DbSession = Annotated[Session, Depends(get_db)]

# Kept in sync with main.py's FastAPI(version=...).
APP_VERSION = "0.1.0"


@router.get(
    "/monitoring",
    response_model=MonitoringResponse,
    summary="Basic application and database health",
)
def get_monitoring(
    db: DbSession,
    current_user: Annotated[User, Depends(require_role(Role.ADMIN))],
) -> MonitoringResponse:
    """Return basic app status and a database connectivity check.

    The database check runs a trivial ``SELECT 1``. Any failure (DB down,
    connection refused, etc.) is reported as ``status: "error"`` without
    exposing the underlying exception to the client.
    """
    db_ok = False
    db_error = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        # Do NOT leak the underlying exception message to clients.
        db_ok = False
        db_error = True

    return MonitoringResponse(
        application="SIH26033 Backend",
        version=APP_VERSION,
        status="ok" if db_ok else "degraded",
        timestamp=datetime.now(timezone.utc),
        database={
            "status": "connected" if db_ok else "unavailable",
            "error": db_error,
        },
    )
