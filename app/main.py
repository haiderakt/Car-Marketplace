from fastapi import FastAPI
from app.routers import users, cars, auth

app=FastAPI()

app.include_router(users.router, prefix="/users")
app.include_router(cars.router, prefix="/cars")
app.include_router(auth.router, prefix="/auth")