from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.car import Car
from app.models.purchase_inquiry import PurchaseInquiry
from app.models.user import User
from app.schemas.purchase_inquiry import PurchaseInquiryCreate, PurchaseInquiryResponse, PurchaseInquiryStatusUpdate

router = APIRouter()

@router.post("/", response_model=PurchaseInquiryResponse, status_code=201)
def create_purchase_inquiry(inquiry_data: PurchaseInquiryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car = db.query(Car).filter(Car.id == inquiry_data.car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.listing_type not in ["sale", "both"]:
        raise HTTPException(status_code=400, detail="This car is not listed for sale")

    if car.owner_id == current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="You cannot inquire about your own car")

    new_inquiry = PurchaseInquiry(
        car_id = car.id,
        buyer_id = current_user.id,
        message = inquiry_data.message,
        status = "pending",
    )

    try:
        db.add(new_inquiry)
        db.commit()
        db.refresh(new_inquiry)
    except Exception:
        db.rollback()
        raise

    return new_inquiry


@router.get("/mine", response_model=list[PurchaseInquiryResponse])
def get_my_purchase_inquiries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(PurchaseInquiry)
    if current_user.role != "admin":
        query = query.filter(PurchaseInquiry.buyer_id == current_user.id)
    inquiries = query.order_by(PurchaseInquiry.id.desc()).all()

    return inquiries

@router.get("/for-my-cars", response_model=list[PurchaseInquiryResponse])
def get_inquiries_for_my_cars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(PurchaseInquiry).join(Car, PurchaseInquiry.car_id == Car.id)
    if current_user.role != "admin":
        query = query.filter(Car.owner_id == current_user.id)
    inquiries = query.order_by(PurchaseInquiry.id.desc()).all()

    return inquiries


@router.patch("/{inquiry_id}/status", response_model=PurchaseInquiryResponse)
def update_purchase_inquiry_status(
    inquiry_id: int,
    status_data: PurchaseInquiryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inquiry = (
        db.query(PurchaseInquiry)
        .filter(PurchaseInquiry.id == inquiry_id)
        .first()
    )

    if inquiry is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase inquiry not found",
        )

    car = db.query(Car).filter(Car.id == inquiry.car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )

    if car.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the car's owner can update this inquiry",
        )

    if inquiry.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending inquiries can be accepted or rejected",
        )

    inquiry.status = status_data.status

    try:
        db.commit()
        db.refresh(inquiry)
    except Exception:
        db.rollback()
        raise

    return inquiry