"""
Dars 13 — ORM Models, Relationship, ForeignKey (Storely)
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db
from app.models import Category, Product   # MUHIM: import qilinishi shart,
                                             # aks holda create_all() ularni "ko'rmaydi"

app = FastAPI(title="Storely ORM Models demo", version="1.0.0")

# Jadvallarni yaratish (faqat o'rganish uchun — Dars 14'dan Alembic ishlatiladi)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Storely ORM Models demo ishlamoqda"}


@app.get("/tables-check", tags=["Debug"])
def check_tables(db: Session = Depends(get_db)):
    """Jadvallar haqiqatan yaratilganini tekshirish."""
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    return {"tables": tables}


@app.post("/seed-demo-data", tags=["Debug"])
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Demo ma'lumot qo'shish — relationship qanday ishlashini ko'rish uchun.
    (To'liq CRUD Dars 15'da o'rganiladi, bu — faqat oldindan ko'rish)
    """
    category = Category(name="Elektronika", description="Elektron qurilmalar")
    db.add(category)
    db.commit()
    db.refresh(category)   # DB tomonidan berilgan id'ni Python obyektiga yuklaydi

    product1 = Product(name="Simli sichqoncha", price=45000, quantity=15, category_id=category.id)
    product2 = Product(name="Klaviatura", price=120000, quantity=8, category_id=category.id)
    db.add_all([product1, product2])
    db.commit()

    return {
        "category": category.name,
        "products_added": [product1.name, product2.name],
    }


@app.get("/category-with-products", tags=["Debug"])
def category_with_products(db: Session = Depends(get_db)):
    """relationship() orqali kategoriya va uning mahsulotlarini birga olish."""
    category = db.query(Category).first()
    if not category:
        return {"message": "Hali kategoriya yo'q. Avval /seed-demo-data ni chaqiring"}

    return {
        "category": category.name,
        "products": [p.name for p in category.products],   # relationship ishlatilyapti!
    }


# Ishga tushirish: python -m uvicorn app.main:app --reload
#
# Tartib bilan sinab ko'ring:
# 1. http://127.0.0.1:8000/tables-check          <- "categories", "products" ko'rinishi kerak
# 2. POST http://127.0.0.1:8000/seed-demo-data    <- /docs orqali chaqiring
# 3. http://127.0.0.1:8000/category-with-products <- relationship natijasi