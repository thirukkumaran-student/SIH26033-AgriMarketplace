"""add forecasts table

Revision ID: 315606f9e7b2
Revises: 76f7011ef89e
Create Date: 2026-09-07 18:15:54.219178

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "315606f9e7b2"
down_revision: Union[str, Sequence[str], None] = "76f7011ef89e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forecasts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("crop", sa.String(length=100), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("predicted_demand", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_forecasts_id",
        "forecasts",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_forecasts_id", table_name="forecasts")
    op.drop_table("forecasts")