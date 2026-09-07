from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.orders import router as orders_router
from app.api.v1.restaurants import router as restaurants_router

app = FastAPI(title="Delivery API")

app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(restaurants_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}