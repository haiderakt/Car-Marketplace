"""add purchase inquiry messages

Revision ID: 7c4b9f2d1e6a
Revises: 21006c4c2a94
Create Date: 2026-10-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c4b9f2d1e6a"
down_revision: Union[str, Sequence[str], None] = "21006c4c2a94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "purchase_inquiry_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("inquiry_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["inquiry_id"],
            ["purchase_inquiries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO purchase_inquiry_messages (inquiry_id, sender_id, message)
            SELECT id, buyer_id, message
            FROM purchase_inquiries
            WHERE message IS NOT NULL AND message != ''
            """
        )
    )


def downgrade() -> None:
    op.drop_table("purchase_inquiry_messages")
