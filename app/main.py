from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.routers import users, cars, auth

app=FastAPI()

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(users.router, prefix="/users")
app.include_router(cars.router, prefix="/cars")
app.include_router(auth.router, prefix="/auth")