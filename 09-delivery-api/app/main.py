from fastapi import FastAPI

from app.api.v1.auth import router as auth_router

app = FastAPI(title="Delivery API")

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}