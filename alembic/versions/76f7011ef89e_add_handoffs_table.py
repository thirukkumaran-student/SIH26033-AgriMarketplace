"""add handoffs table

Revision ID: 76f7011ef89e
Revises: f22e87c8b2a0
Create Date: 2026-09-07 17:16:16.806947

"""


from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "76f7011ef89e"
down_revision: Union[str, Sequence[str], None] = "f22e87c8b2a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "handoffs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shipment_id", sa.Integer(), nullable=False),
        sa.Column("from_party", sa.String(), nullable=False),
        sa.Column("to_party", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("remarks", sa.String(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["shipment_id"],
            ["shipments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_handoffs_id"),
        "handoffs",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_handoffs_shipment_id"),
        "handoffs",
        ["shipment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_handoffs_shipment_id"),
        table_name="handoffs",
    )

    op.drop_index(
        op.f("ix_handoffs_id"),
        table_name="handoffs",
    )

    op.drop_table("handoffs")
