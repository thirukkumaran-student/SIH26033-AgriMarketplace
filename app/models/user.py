"""The shared User ORM model.

Exactly ONE ``users`` table exists for every role (FARMER, CONSUMER,
BULK_BUYER, FINANCIER, LOGISTICS, ADMIN). Feature modules must never create
their own user tables or authentication systems.

The login identifier varies by role:
- FARMER logs in with ``phone`` (email is optional)
- every other role logs in with ``email`` (phone is not used)

``email`` and ``phone`` are both optional at the database level so that a
farmer without an email (or a future user without a phone) can exist, but
every user must have at least one of them.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.farmer import FarmerProfile, VerificationDocument
    from app.models.consumer import ConsumerProfile
from app.core.enums import Role

# Comma separated list of quoted values, e.g. 'FARMER', 'CONSUMER', ...
VALID_ROLE_VALUES = ", ".join(f"'{role.value}'" for role in Role)


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        # Database-level guard so an invalid role can never be stored.
        CheckConstraint(f"role IN ({VALID_ROLE_VALUES})", name="ck_users_role"),
        # Every user must have at least one login identifier.
        CheckConstraint(
            "email IS NOT NULL OR phone IS NOT NULL",
            name="ck_users_identifier",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Nullable so farmers can register with phone only. Unique when present.
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    # Nullable for non-farmers. Unique when present. This is the auth
    # identifier for FARMER accounts (distinct from farmer_profiles.phone).
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, unique=True, index=True
    )
    # NEVER a plaintext password. Only the bcrypt hash lives in the database.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Stores one of the Role values (as a string) defined in app/core/enums.py.
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    # Set automatically by the database when the row is inserted.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # ORM relationships (lazy-loaded, imported only for type checking above)
    farmer_profile: Mapped["FarmerProfile | None"] = relationship(back_populates="user", uselist=False)
    consumer_profile: Mapped["ConsumerProfile | None"] = relationship(back_populates="user", uselist=False)
    # verification_documents relationship removed to avoid FK ambiguity
    # (user_id + reviewed_by both point to users.id). Use explicit queries instead.

    def __repr__(self) -> str:
        # Custom repr: never include the password hash by accident.
        return f"<User id={self.id} email={self.email!r} phone={self.phone!r} role={self.role!r}>"
