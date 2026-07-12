from fastapi import FastAPI
from app.config import get_settings
from app.routers import health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
)

app.include_router(health.router, tags=["Health"])

@app.get("/")
def root():
    return {"message": f"{settings.app_name} ishlamoqda", "debug": settings.debug}

# Ishga tushirish:
# # python -m uvicorn app.main:app --reload