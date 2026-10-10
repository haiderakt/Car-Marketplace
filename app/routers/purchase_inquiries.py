from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.car import Car
from app.models.purchase_inquiry import PurchaseInquiry
from app.models.purchase_inquiry_message import PurchaseInquiryMessage
from app.models.user import User
from app.schemas.purchase_inquiry import (
    PurchaseInquiryCreate,
    PurchaseInquiryMessageCreate,
    PurchaseInquiryMessageResponse,
    PurchaseInquiryResponse,
    PurchaseInquiryStatusUpdate,
)

router = APIRouter()

@router.post("/", response_model=PurchaseInquiryResponse, status_code=201)
def create_purchase_inquiry(inquiry_data: PurchaseInquiryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car = db.query(Car).filter(Car.id == inquiry_data.car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.is_sold:
        raise HTTPException(status_code=400, detail="This car has already been sold")

    if car.listing_type not in ["sale", "both"]:
        raise HTTPException(status_code=400, detail="This car is not listed for sale")

    if car.owner_id == current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="You cannot inquire about your own car")

    accepted_inquiry = (
        db.query(PurchaseInquiry)
        .filter(PurchaseInquiry.car_id == car.id)
        .filter(PurchaseInquiry.status == "accepted")
        .first()
    )

    if accepted_inquiry is not None:
        raise HTTPException(
            status_code=400,
            detail="This car already has an accepted inquiry",
        )

    existing_inquiry = (
        db.query(PurchaseInquiry)
        .filter(PurchaseInquiry.car_id == car.id)
        .filter(PurchaseInquiry.buyer_id == current_user.id)
        .filter(PurchaseInquiry.status.in_(["pending", "accepted"]))
        .first()
    )

    if existing_inquiry is not None:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending or accepted inquiry for this car",
        )

    new_inquiry = PurchaseInquiry(
        car_id = car.id,
        buyer_id = current_user.id,
        seller_id = car.owner_id,
        message = inquiry_data.message,
        status = "pending",
    )

    try:
        db.add(new_inquiry)
        db.flush()

        if inquiry_data.message:
            db.add(
                PurchaseInquiryMessage(
                    inquiry_id=new_inquiry.id,
                    sender_id=current_user.id,
                    message=inquiry_data.message,
                )
            )

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
    query = db.query(PurchaseInquiry)
    if current_user.role != "admin":
        query = query.filter(PurchaseInquiry.seller_id == current_user.id)
    inquiries = query.order_by(PurchaseInquiry.id.desc()).all()

    return inquiries


@router.get(
    "/{inquiry_id}/messages",
    response_model=list[PurchaseInquiryMessageResponse],
)
def get_purchase_inquiry_messages(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inquiry = db.query(PurchaseInquiry).filter(PurchaseInquiry.id == inquiry_id).first()

    if inquiry is None:
        raise HTTPException(status_code=404, detail="Purchase inquiry not found")

    car = db.query(Car).filter(Car.id == inquiry.car_id).first()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if (
        inquiry.buyer_id != current_user.id
        and inquiry.seller_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the buyer or seller can view these messages",
        )

    return (
        db.query(PurchaseInquiryMessage)
        .filter(PurchaseInquiryMessage.inquiry_id == inquiry.id)
        .order_by(PurchaseInquiryMessage.id.asc())
        .all()
    )


@router.post(
    "/{inquiry_id}/messages",
    response_model=PurchaseInquiryMessageResponse,
    status_code=201,
)
def create_purchase_inquiry_message(
    inquiry_id: int,
    message_data: PurchaseInquiryMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inquiry = db.query(PurchaseInquiry).filter(PurchaseInquiry.id == inquiry_id).first()

    if inquiry is None:
        raise HTTPException(status_code=404, detail="Purchase inquiry not found")

    car = db.query(Car).filter(Car.id == inquiry.car_id).first()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if (
        inquiry.buyer_id != current_user.id
        and inquiry.seller_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the buyer or seller can send messages",
        )

    if inquiry.status in ["rejected", "completed"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot send messages to a closed inquiry",
        )

    new_message = PurchaseInquiryMessage(
        inquiry_id=inquiry.id,
        sender_id=current_user.id,
        message=message_data.message,
    )

    try:
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
    except Exception:
        db.rollback()
        raise

    return new_message


@router.post(
    "/{inquiry_id}/complete",
    response_model=PurchaseInquiryResponse,
)
def complete_purchase(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inquiry = db.query(PurchaseInquiry).filter(PurchaseInquiry.id == inquiry_id).first()

    if inquiry is None:
        raise HTTPException(status_code=404, detail="Purchase inquiry not found")

    if inquiry.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the seller can confirm this purchase",
        )

    if inquiry.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail="Only accepted inquiries can be completed",
        )

    car = (
        db.query(Car)
        .filter(Car.id == inquiry.car_id)
        .with_for_update()
        .first()
    )

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.is_sold:
        raise HTTPException(status_code=400, detail="This car has already been sold")

    if car.listing_type not in ["sale", "both"]:
        raise HTTPException(
            status_code=400,
            detail="This car is no longer listed for sale",
        )

    try:
        car.is_sold = True
        car.sold_at = datetime.now(timezone.utc)
        car.owner_id = inquiry.buyer_id
        inquiry.status = "completed"

        other_inquiries = (
            db.query(PurchaseInquiry)
            .filter(PurchaseInquiry.car_id == car.id)
            .filter(PurchaseInquiry.id != inquiry.id)
            .filter(PurchaseInquiry.status.in_(["pending", "accepted"]))
            .all()
        )

        for other_inquiry in other_inquiries:
            other_inquiry.status = "rejected"

        db.commit()
        db.refresh(inquiry)
    except Exception:
        db.rollback()
        raise

    return inquiry


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

    if car.is_sold or car.listing_type not in ["sale", "both"]:
        raise HTTPException(
            status_code=400,
            detail="This car is no longer available for sale",
        )

    if inquiry.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the car's owner can update this inquiry",
        )

    if inquiry.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending inquiries can be accepted or rejected",
        )

    if status_data.status == "accepted":
        existing_accepted = (
            db.query(PurchaseInquiry)
            .filter(PurchaseInquiry.car_id == inquiry.car_id)
            .filter(PurchaseInquiry.id != inquiry.id)
            .filter(PurchaseInquiry.status == "accepted")
            .first()
        )

        if existing_accepted is not None:
            raise HTTPException(
                status_code=400,
                detail="This car already has an accepted inquiry",
            )

    inquiry.status = status_data.status

    try:
        db.commit()
        db.refresh(inquiry)
    except Exception:
        db.rollback()
        raise

    return inquiry