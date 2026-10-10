"""add car sale tracking

Revision ID: 81af42d6ce90
Revises: 7c4b9f2d1e6a
Create Date: 2026-10-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "81af42d6ce90"
down_revision: Union[str, Sequence[str], None] = "7c4b9f2d1e6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cars",
        sa.Column(
            "is_sold",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "cars",
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "purchase_inquiries",
        sa.Column(
            "seller_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                name="fk_purchase_inquiries_seller_id_users",
            ),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE purchase_inquiries
            SET seller_id = (
                SELECT owner_id
                FROM cars
                WHERE cars.id = purchase_inquiries.car_id
            )
            """
        )
    )

    op.alter_column(
        "purchase_inquiries",
        "seller_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("purchase_inquiries", "seller_id")
    op.drop_column("cars", "sold_at")
    op.drop_column("cars", "is_sold")
