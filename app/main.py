from fastapi import FastAPI
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.routers import users, cars, auth, rentals, purchase_inquiries, car_images
from fastapi.openapi.utils import get_openapi

app=FastAPI()

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(rentals.router, prefix="/rentals", tags=["Rentals"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(purchase_inquiries.router, prefix="/purchase-inquiries",tags=["Purchase Inquiries"])
app.include_router(car_images.router, prefix="/cars")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    for component in schema.get("components", {}).get("schemas", {}).values():
        for prop in component.get("properties", {}).values():
            if prop.get("contentMediaType") == "application/octet-stream":
                prop.pop("contentMediaType", None)
                prop["format"] = "binary"

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi