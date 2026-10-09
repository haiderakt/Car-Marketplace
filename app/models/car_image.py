from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class CarImage(Base):
    __tablename__ = "car_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"))
    original_path: Mapped[str] = mapped_column(String(500))
    optimized_path: Mapped[str] = mapped_column(String(500))

    
