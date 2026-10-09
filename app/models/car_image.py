from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.car import Car

from app.database import Base

class CarImage(Base):
    __tablename__ = "car_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    car: Mapped["Car"] = relationship(back_populates="images")
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"))
    original_path: Mapped[str] = mapped_column(String(500))
    optimized_path: Mapped[str] = mapped_column(String(500))

    @property
    def original_url(self) -> str:
        return "/" + self.original_path.replace("\\", "/")


    @property
    def optimized_url(self) -> str:
        return "/" + self.optimized_path.replace("\\", "/")

    
