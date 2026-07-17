"""
Dars 15 — CRUD (Storely)
Alembic orqali boshqariladigan jadvallar + to'liq CRUD endpointlar.
"""

from fastapi import FastAPI

from app.routers import product, category

app = FastAPI(title="Storely CRUD", version="1.0.0")

app.include_router(category.router)
app.include_router(product.router)


@app.get("/")
def root():
    return {"message": "Storely CRUD demo ishlamoqda"}


# Ishga tushirish: python -m uvicorn app.main:app --reload