from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db
from app.models import customer, order 

# exercise/app/main.py

# Base.metadata.create_all(bind=engine) chaqiring
# GET "/tables-check" — jadvallar ro'yxatini qaytarsin
# POST "/seed-demo-data" — 1 ta mijoz va shu mijozning 2 ta buyurtmasini qo'shsin
# GET "/customer-with-orders" — birinchi mijozni uning buyurtmalari bilan birga qaytarsin

app = FastAPI(title=("Storely ORM Models demo"), version="1.0.0")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Storely ORM Models demo ishlamoqda."}


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
    """
    customer1 = customer.Customer(full_name="Ali Valiyev", phone="+998901234567")
    db.add(customer1)
    db.commit()
    db.refresh(customer1)  # DB tomonidan berilgan id'ni Python obyektiga yuklaydi

    order1 = order.Order(total_amount=150000, status="pending", customer_id=customer1.id)
    order2 = order.Order(total_amount=250000, status="completed", customer_id=customer1.id)
    db.add_all([order1, order2])
    db.commit()

    return {
        "customer": customer1.full_name,
        "orders_added": [order1.id, order2.id],
    }

@app.get("/customer-with-orders", tags=["Debug"])
def customer_with_orders(db: Session = Depends(get_db)):
    """relationship() orqali mijoz va uning buyurtmlarini birga olish."""
    customer_obj = db.query(customer.Customer).first()
    if not customer_obj:
        return {"message": "Hali mijoz yo'q. Avval /seed-demo-data ni chaqiring"}

    return {
        "customer": customer_obj.full_name,
        "orders": [{"id": order.id, "total_amount": order.total_amount, "status": order.status} for order in customer_obj.orders]
    }


@app.get("/customer-with-orders/{customer_id}", tags=["Debug"])
def customer_with_orders_by_id(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer by id together with their orders."""
    customer_obj = db.query(customer.Customer).filter(customer.Customer.id == customer_id).first()
    if not customer_obj:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer": customer_obj.full_name,
        "orders": [{"id": order.id, "total_amount": order.total_amount, "status": order.status} for order in customer_obj.orders]
    }

# Ishga tushirish: python -m uvicorn app.main:app --reload
#
# Tartib bilan sinab ko'ring:
# 1. http://127.0.0.1:8000/tables-check          <- "categories", "products" ko'rinishi kerak
# 2. POST http://127.0.0.1:8000/seed-demo-data    <- /docs orqali chaqiring
# 3. http://127.0.0.1:8000/order-with-customer <- relationship natijasi