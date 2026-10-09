from pydantic import BaseModel, ConfigDict


class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    price: int

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

    class Config:
        from_attributes = True

class CarUpdate(BaseModel):
    make: str
    model: str
    year: int
    price: int


