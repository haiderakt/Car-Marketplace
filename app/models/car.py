from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.user import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.car_image import CarImage

from app.database import Base


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship()
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int]
    price: Mapped[int]
    listing_type: Mapped[str] = mapped_column(String(10),default="both", nullable=False)
    rental_price_per_day: Mapped[int | None] = mapped_column(nullable=True)
    images: Mapped[list["CarImage"]] = relationship(
    back_populates="car",
    cascade="all, delete-orphan",
)