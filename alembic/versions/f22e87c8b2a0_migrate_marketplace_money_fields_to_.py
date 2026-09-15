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
    _change_money_type("produce", "price_per_unit", sa.Float(), sa.Numeric(12, 2), "price_per_unit::numeric(12,2)")
    _change_money_type("orders", "unit_price", sa.Float(), sa.Numeric(12, 2), "unit_price::numeric(12,2)")
    _change_money_type("orders", "total_amount", sa.Float(), sa.Numeric(12, 2), "total_amount::numeric(12,2)")
    _change_money_type("shipments", "logistics_cost", sa.Float(), sa.Numeric(12, 2), "logistics_cost::numeric(12,2)")


def downgrade() -> None:
    _change_money_type("shipments", "logistics_cost", sa.Numeric(12, 2), sa.Float(), "logistics_cost::double precision")
    _change_money_type("orders", "total_amount", sa.Numeric(12, 2), sa.Float(), "total_amount::double precision")
    _change_money_type("orders", "unit_price", sa.Numeric(12, 2), sa.Float(), "unit_price::double precision")
    _change_money_type("produce", "price_per_unit", sa.Numeric(12, 2), sa.Float(), "price_per_unit::double precision")


def _change_money_type(table: str, column: str, existing_type, new_type, postgres_using: str) -> None:
    """Use native ALTER on PostgreSQL and a safe table rebuild on SQLite."""
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(column, existing_type=existing_type, type_=new_type, existing_nullable=False)
        return

    op.alter_column(
        table,
        column,
        existing_type=existing_type,
        type_=new_type,
        existing_nullable=False,
        postgresql_using=postgres_using,
    )
