"""
Dars 11 — Project Structure va Config
"""

from fastapi import FastAPI
from app.config import get_settings
from app.routers import info

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
)

app.include_router(info.router, tags=["Config"])


@app.get("/")
def root():
    return {"message": f"{settings.app_name} ishlamoqda", "debug": settings.debug}


# Ishga tushirish (DIQQAT: endi app papkasi ichida bo'lgani uchun):
# python -m uvicorn app.main:app --reload