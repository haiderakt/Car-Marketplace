from datetime import date
from pydantic import BaseModel, ConfigDict

class RentalCreate(BaseModel):
    car_id: int
    start_date: date
    end_date: date

class RentalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    car_id: int
    renter_id: int
    start_date: date
    end_date: date
    total_price: int
    status: str