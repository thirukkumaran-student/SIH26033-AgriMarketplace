"""The shared User ORM model.

Exactly ONE ``users`` table exists for every role (FARMER, CONSUMER,
BULK_BUYER, FINANCIER, LOGISTICS, ADMIN). Feature modules must never create
their own user tables or authentication systems.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.farmer import FarmerProfile, VerificationDocument
    from app.models.consumer import ConsumerProfile
    from app.models.buyer import BuyerProfile
    from app.models.financier import FinancierProfile

from app.core.enums import Role

# Comma separated list of quoted values, e.g. 'FARMER', 'CONSUMER', ...
VALID_ROLE_VALUES = ", ".join(f"'{role.value}'" for role in Role)


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        # Database-level guard so an invalid role can never be stored.
        CheckConstraint(f"role IN ({VALID_ROLE_VALUES})", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
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
    farmer_profile: Mapped["FarmerProfile | None"] = relationship(
    back_populates="user",
    uselist=False,
)

    consumer_profile: Mapped["ConsumerProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
    )

    buyer_profile: Mapped["BuyerProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
    )

    financier_profile: Mapped["FinancierProfile | None"] = relationship(
    back_populates="user",
    uselist=False,
    )
    # verification_documents relationship removed to avoid FK ambiguity
    # (user_id + reviewed_by both point to users.id). Use explicit queries instead.

    def __repr__(self) -> str:
        # Custom repr: never include the password hash by accident.
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
