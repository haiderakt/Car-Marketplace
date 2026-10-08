from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_cars():
    return {"message": "testing"}