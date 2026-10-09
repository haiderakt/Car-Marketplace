from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.image_utils import create_optimized_image
from app.models import Car, CarImage, User

router = APIRouter()

ORIGINALS_DIR = Path("uploads/cars/originals")
MAX_FILE_SIZE = 10*1024*1024 #10mb
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}




@router.post("/cars/{car_id}/images")
async def upload_car_image(car_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car = db.query(Car).filter(Car.id == car_id).first()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only upload images of your own car")

    image_id = str(uuid4())
    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
    original_path = ORIGINALS_DIR / f"{image_id}.upload"

    contents = await file.read(MAX_FILE_SIZE + 1)

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image must be 10mb or smaller"
        )

    try:
        from io import BytesIO

        with Image.open(BytesIO(contents)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=415,
                    detail="Only JPEG, PNG and WenP images are allowed",
                )
            image.verify()

    except(UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image format"
        )