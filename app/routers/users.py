from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.security import password_hash
from app.auth import get_current_user
from sqlalchemy.exc import IntegrityError

router = APIRouter()



@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username = user.username,
        email = user.email,
        password = password_hash.hash(user.password),
        role = "user",
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user