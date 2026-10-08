from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Car, User
from app.schemas.car import CarCreate, CarResponse, CarUpdate
from app.auth import get_current_user

router = APIRouter()



@router.get("/", response_model=list[CarResponse])
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(Car).all()

    return cars


@router.post("/", response_model=CarResponse)
def create_car(car: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_car = Car(
        owner_id = current_user.id,
        make = car.make,
        model=car.model,
        year=car.year,
        price=car.price,
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id==car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found"
        )

    return car

@router.put("/{car_id}", response_model=CarUpdate)
def update_car(car_id: int, car: CarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car_to_update = db.query(Car).filter(Car.id==car_id).first()

    if car_to_update is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )

    if car_to_update.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own cars",
        )

    car_to_update.make = car.make
    car_to_update.model = car.model
    car_to_update.year = car.year
    car_to_update.price = car.price

    db.commit()
    db.refresh(car_to_update)

    return car_to_update