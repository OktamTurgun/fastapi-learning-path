"""
Dars 12 — SQLAlchemy Engine va Session
"""

from fastapi import FastAPI
from app.routers import db_demo

app = FastAPI(title="SQLAlchemy Engine/Session demo", version="1.0.0")

app.include_router(db_demo.router, tags=["Database"])


@app.get("/")
def root():
    return {"message": "Dars 12 — SQLAlchemy demo ishlamoqda"}


# Ishga tushirish: python -m uvicorn app.main:app --reload
#
# Sinab ko'ring:
# http://127.0.0.1:8000/db-check
# http://127.0.0.1:8000/db-session-info
#
# Ishga tushirgach, papkada "dars12_demo.db" fayli PAYDO BO'LGANINI
# tekshiring — bu SQLite ma'lumotlar bazasi fayli, Engine tomonidan
# avtomatik yaratiladi.