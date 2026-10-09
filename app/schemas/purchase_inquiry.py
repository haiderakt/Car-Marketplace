from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class PurchaseInquiryCreate(BaseModel):
    car_id: int
    message: str | None = Field(default=None, max_length=2000)

class PurchaseInquiryStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected"]

class PurchaseInquiryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    car_id: int
    buyer_id: int
    message: str | None
    status: str