"""Shared pytest fixtures.

Tests run against a disposable SQLite database file by default, so the whole
suite works without PostgreSQL installed. Point TEST_DATABASE_URL at a real
(dedicated test) PostgreSQL database to run against Postgres instead:

    TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/sih26033_test pytest
"""

import os

# Environment variables MUST be set before app modules are imported, because
# the app builds its engine / settings from them at import time.
test_db_url = os.environ.get("TEST_DATABASE_URL")
os.environ["DATABASE_URL"] = test_db_url if test_db_url else "sqlite:///./test_auth.db"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256-hmac-0123456789")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402  (imports models so metadata is populated)


@pytest.fixture(autouse=True)
def clean_database():
    """Give every test empty tables.

    Only touches the test database the engine points at (the disposable
    SQLite file, or whatever TEST_DATABASE_URL names).
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:  # context manager triggers lifespan
        yield test_client
