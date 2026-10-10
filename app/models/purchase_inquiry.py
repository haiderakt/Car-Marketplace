from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PurchaseInquiry(Base):
    __tablename__ = "purchase_inquiries"

    id: Mapped[int] = mapped_column(primary_key=True)

    car_id: Mapped[int] = mapped_column(
        ForeignKey("cars.id", ondelete="CASCADE"),
        nullable=False,
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="fk_purchase_inquiries_seller_id_users"),
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )