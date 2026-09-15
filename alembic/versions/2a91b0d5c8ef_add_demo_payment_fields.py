"""add demo payment fields

Revision ID: 2a91b0d5c8ef
Revises: 315606f9e7b2
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2a91b0d5c8ef"
down_revision: Union[str, Sequence[str], None] = "315606f9e7b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.add_column(
            sa.Column("payment_status", sa.String(length=20), server_default="UNPAID", nullable=False)
        )
        batch_op.add_column(sa.Column("payment_method", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("payment_reference", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("shipments") as batch_op:
        batch_op.add_column(
            sa.Column("logistics_fee_status", sa.String(length=20), server_default="DUE", nullable=False)
        )
        batch_op.add_column(sa.Column("logistics_fee_reference", sa.String(length=30), nullable=True))
        batch_op.add_column(
            sa.Column("logistics_fee_collected_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("shipments") as batch_op:
        batch_op.drop_column("logistics_fee_collected_at")
        batch_op.drop_column("logistics_fee_reference")
        batch_op.drop_column("logistics_fee_status")

    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_column("paid_at")
        batch_op.drop_column("payment_reference")
        batch_op.drop_column("payment_method")
        batch_op.drop_column("payment_status")
