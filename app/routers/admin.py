from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models import Car, CarImage, PurchaseInquiry, PurchaseInquiryMessage, Rental, User
from app.schemas.admin import AdminPasswordUpdate, AdminRoleUpdate
from app.schemas.car import CarResponse
from app.schemas.user import UserResponse
from app.security import password_hash

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(User).order_by(User.id.desc()).all()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    if user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="You cannot delete the last admin",
            )

    owned_car_ids = [
        car_id
        for (car_id,) in db.query(Car.id).filter(Car.owner_id == user.id).all()
    ]

    try:
        db.query(PurchaseInquiryMessage).filter(
            PurchaseInquiryMessage.sender_id == user.id
        ).delete(synchronize_session=False)

        inquiry_query = db.query(PurchaseInquiry).filter(
            or_(
                PurchaseInquiry.buyer_id == user.id,
                PurchaseInquiry.seller_id == user.id,
            )
        )
        if owned_car_ids:
            inquiry_query = db.query(PurchaseInquiry).filter(
                or_(
                    PurchaseInquiry.buyer_id == user.id,
                    PurchaseInquiry.seller_id == user.id,
                    PurchaseInquiry.car_id.in_(owned_car_ids),
                )
            )
        inquiry_query.delete(synchronize_session=False)

        rental_query = db.query(Rental).filter(Rental.renter_id == user.id)
        if owned_car_ids:
            rental_query = db.query(Rental).filter(
                or_(
                    Rental.renter_id == user.id,
                    Rental.car_id.in_(owned_car_ids),
                )
            )
        rental_query.delete(synchronize_session=False)

        if owned_car_ids:
            db.query(CarImage).filter(
                CarImage.car_id.in_(owned_car_ids)
            ).delete(synchronize_session=False)
            db.query(Car).filter(Car.id.in_(owned_car_ids)).delete(
                synchronize_session=False
            )

        db.delete(user)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"detail": "User deleted successfully"}


@router.put("/users/{user_id}/password")
def update_user_password(
    user_id: int,
    password_data: AdminPasswordUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = password_hash.hash(password_data.new_password)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"detail": "User password updated successfully"}


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: AdminRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and role_data.role != "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="You cannot remove the last admin",
            )

    user.role = role_data.role

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user


@router.get("/cars", response_model=list[CarResponse])
def get_all_cars(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return db.query(Car).order_by(Car.id.desc()).all()


@router.delete("/cars/{car_id}")
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    car = db.query(Car).filter(Car.id == car_id).first()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    try:
        db.delete(car)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"detail": "Car deleted successfully"}
