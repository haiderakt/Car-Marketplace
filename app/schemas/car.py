from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal


class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    price: int = Field(gt=0)

    listing_type: Literal["sale", "rent", "both"] = "both"
    rental_price_per_day: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_listing_prices(self):
        if self.listing_type in ["rent", "both"]:
            if self.rental_price_per_day is None:
                raise ValueError(
                    "Rental price per day is required for rental listings"
                )

        return self

class CarImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    car_id: int
    original_url: str
    optimized_url: str

class CarResponse(BaseModel):
    id: int
    owner_id: int
    make: str
    model: str
    year: int
    images: list[CarImageResponse] = []
    price: int
    listing_type: Literal["sale", "rent", "both"]
    rental_price_per_day: int | None

    class Config:
        from_attributes = True

class CarUpdate(BaseModel):
    make: str
    model: str
    year: int
    price: int
    listing_type: Literal["sale", "rent", "both"] = "both"
    rental_price_per_day: int | None = None


