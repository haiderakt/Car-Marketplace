from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Car, User
from app.schemas.car import CarCreate, CarResponse, CarUpdate
from app.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[CarResponse])
def get_cars(db: Session = Depends(get_db),
             make: str | None = None, model: str | None = None, year: int | None = None,
             skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100),
             sort_by: str = Query(default="id"),
             sort_order: str = Query(default="asc")):
    query = db.query(Car)

    if make is not None:
        query = query.filter(Car.make == make)

    if model is not None:
        query = query.filter(Car.model == model)

    if year is not None:
        query = query.filter(Car.year == year)

    if sort_by not in ["id", "make", "model", "year", "price"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort field",
        )

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort order",
        )

    if sort_order == "asc":
        query = query.order_by((getattr(Car, sort_by).asc()))
    else:
        query = query.order_by((getattr(Car, sort_by).desc()))


    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=CarResponse)
def create_car(car: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_car = Car(
        owner_id = current_user.id,
        make = car.make,
        model=car.model,
        year=car.year,
        price=car.price,
        listing_type=car.listing_type,
        rental_price_per_day=car.rental_price_per_day,
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car

@router.get("/for-sale", response_model=list[CarResponse])
def get_cars_for_sale(db: Session = Depends(get_db), skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return (db.query(Car).filter(Car.listing_type.in_(["sale", "both"])).order_by(Car.id.desc()).offset(skip).limit(limit).all())

@router.get("/for-rent", response_model=list[CarResponse])
def get_cars_for_rent(db: Session = Depends(get_db), skip: int = Query(default=0, ge=0),
                      limit: int = Query(default=10, ge=1, le=100)):
    return (
        db.query(Car)
        .filter(Car.listing_type.in_(["rent", "both"]))
        .filter(Car.rental_price_per_day.is_not(None))
        .order_by(Car.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/my-listings", response_model=list[CarResponse])
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Car)
    if current_user.role != "admin":
        query = query.filter(Car.owner_id == current_user.id)

    return query.order_by(Car.id.desc()).all()

@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id==car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    return car

@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car: CarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car_to_update = db.query(Car).filter(Car.id==car_id).first()

    if car_to_update is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )

    if car_to_update.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update your own cars",
        )

    car_to_update.make = car.make
    car_to_update.model = car.model
    car_to_update.year = car.year
    car_to_update.price = car.price
    car_to_update.listing_type = car.listing_type
    car_to_update.rental_price_per_day = car.rental_price_per_day

    db.commit()
    db.refresh(car_to_update)

    return car_to_update


@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car = db.query(Car).filter(Car.id==car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )
    if car.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own cars",
        )

    db.delete(car)
    db.commit()

    return {"detail": "Car deleted successfully"}
