from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

from app.schemas.user import UserCreate, UserResponse
from app.security import password_hash

router = APIRouter()



@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username = user.username,
        email = user.email,
        password = password_hash.hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user