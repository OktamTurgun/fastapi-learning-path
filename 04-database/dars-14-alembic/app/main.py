"""
Dars 14 — Alembic bilan boshqariladigan Storely
create_all() endi ISHLATILMAYDI — jadvallar faqat Alembic orqali yaratiladi/o'zgartiriladi.
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.models import Category, Product

app = FastAPI(title="Storely Alembic demo", version="1.0.0")

# MUHIM: Base.metadata.create_all(bind=engine) ENDI CHAQIRILMAYDI!
# Jadvallar `alembic upgrade head` orqali yaratiladi.


@app.get("/")
def root():
    return {"message": "Storely Alembic demo ishlamoqda"}


@app.get("/tables-check", tags=["Debug"])
def check_tables(db: Session = Depends(get_db)):
    """Jadvallar Alembic orqali yaratilganini tekshirish."""
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    return {"tables": tables}


@app.get("/migration-status", tags=["Debug"])
def migration_status(db: Session = Depends(get_db)):
    """Hozirgi qo'llangan migratsiya versiyasini ko'rsatish."""
    result = db.execute(text("SELECT version_num FROM alembic_version"))
    row = result.fetchone()
    return {"current_revision": row[0] if row else None}

@app.get("/products-columns", tags=["Debug"])
def check_product_columns(db: Session = Depends(get_db)):
    """products jadvalidagi barcha ustunlarni ko'rsatish (PRAGMA orqali)."""
    result = db.execute(text("PRAGMA table_info(products)"))
    columns = [{"name": row[1], "type": row[2]} for row in result]
    return {"columns": columns}


# Ishga tushirish tartibi:
# 1. alembic upgrade head          <- jadval yaratish
# 2. python -m uvicorn app.main:app --reload
# 3. http://127.0.0.1:8000/tables-check
# 4. http://127.0.0.1:8000/migration-status