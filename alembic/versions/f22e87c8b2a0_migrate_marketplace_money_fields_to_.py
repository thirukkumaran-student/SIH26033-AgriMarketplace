"""migrate marketplace money fields to numeric

Revision ID: f22e87c8b2a0
Revises: 70d7a0f1364c
Create Date: 2026-09-07 10:18:16.806073
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f22e87c8b2a0"
down_revision: Union[str, Sequence[str], None] = "70d7a0f1364c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "produce",
        "price_per_unit",
        existing_type=sa.Float(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="price_per_unit::numeric(12,2)",
    )

    op.alter_column(
        "orders",
        "unit_price",
        existing_type=sa.Float(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="unit_price::numeric(12,2)",
    )

    op.alter_column(
        "orders",
        "total_amount",
        existing_type=sa.Float(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="total_amount::numeric(12,2)",
    )

    op.alter_column(
        "shipments",
        "logistics_cost",
        existing_type=sa.Float(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="logistics_cost::numeric(12,2)",
    )


def downgrade() -> None:
    op.alter_column(
        "shipments",
        "logistics_cost",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="logistics_cost::double precision",
    )

    op.alter_column(
        "orders",
        "total_amount",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="total_amount::double precision",
    )

    op.alter_column(
        "orders",
        "unit_price",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="unit_price::double precision",
    )

    op.alter_column(
        "produce",
        "price_per_unit",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="price_per_unit::double precision",
    )