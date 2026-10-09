from pydantic import BaseModel


class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    price: int

class CarResponse(BaseModel):
    id: int
    owner_id: int
    make: str
    model: str
    year: int
    price: int

    class Config:
        from_attributes = True

class CarUpdate(BaseModel):
    make: str
    model: str
    year: int
    price: int

class CarImageResponse(BaseModel):
    id: int
    car_id: int
    original_url: str
    optimized_url: str
