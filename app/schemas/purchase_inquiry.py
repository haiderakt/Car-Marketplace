from datetime import datetime
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
    seller_id: int
    message: str | None
    status: str


class PurchaseInquiryMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class PurchaseInquiryMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    inquiry_id: int
    sender_id: int
    message: str
    created_at: datetime