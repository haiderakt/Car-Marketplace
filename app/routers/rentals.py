from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Car, Rental, User
from app.schemas.rental import RentalCreate, RentalResponse

router = APIRouter()


@router.post("/", response_model=RentalResponse, status_code=201)
def create_rental(rental: RentalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if rental.end_date <= rental.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date",
        )

    car = db.query(Car).filter(Car.id == rental.car_id).with_for_update().first()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.owner_id == current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="You cannot rent your own car")

    if car.listing_type not in ["rent", "both"]:
        raise HTTPException(status_code=400, detail="This car is not available for rent")

    if car.rental_price_per_day is None or car.rental_price_per_day <= 0:
        raise HTTPException(status_code=400, detail="This car does not have a valid rental price")

    days = (rental.end_date - rental.start_date).days

    overlapping_rental = db.query(Rental).filter(
        Rental.car_id == car.id,
        Rental.status == "confirmed",
        Rental.start_date < rental.end_date,
        Rental.end_date > rental.start_date,
    ).first()

    if overlapping_rental is not None:
        raise HTTPException(
            status_code=409,
            detail="This car is already booked for some of these dates",
        )
    total_price = days * car.rental_price_per_day

    new_rental = Rental(
        car_id=car.id,
        renter_id=current_user.id,
        start_date=rental.start_date,
        end_date=rental.end_date,
        total_price=total_price,
        status="confirmed",
    )

    try:
        db.add(new_rental)
        db.commit()
        db.refresh(new_rental)
    except Exception:
        db.rollback()
        raise

    return new_rental

@router.get("/", response_model=list[RentalResponse])
def get_my_rentals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Rental)
    if current_user.role != "admin":
        query = query.filter(Rental.renter_id == current_user.id)
    rentals = query.order_by(Rental.start_date.desc()).all()

    return rentals


@router.patch("/{rental_id}/cancel", response_model=RentalResponse)
def cancel_rental(rental_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rental = (db.query(Rental).filter(Rental.id == rental_id).first())

    if rental is None:
        raise HTTPException(
            status_code=404,
            detail="Rental not found",
        )

    if rental.renter_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own rentals",
        )

    if rental.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Only confirmed rentals can be cancelled",
        )

    rental.status = "cancelled"

    db.commit()
    db.refresh(rental)

    return rental