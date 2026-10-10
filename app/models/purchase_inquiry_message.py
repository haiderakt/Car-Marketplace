from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PurchaseInquiryMessage(Base):
    __tablename__ = "purchase_inquiry_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    inquiry_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_inquiries.id", ondelete="CASCADE"),
        nullable=False,
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
