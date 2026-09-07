"""SQLAlchemy setup: engine, session factory, declarative Base and the
reusable ``get_db`` FastAPI dependency.

One engine + one session factory for the whole (modular monolith) app.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite (used by the test suite) needs this flag so the session can be used
# from FastAPI's request handling thread.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # silently drop stale connections (Postgres restarts, ...)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""


def get_db():
    """FastAPI dependency that yields one database session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
