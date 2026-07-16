from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, get_db
from app.models import Customer, Order 

app = FastAPI(title=("Storely Alembic demo"), version="1.0.0")


@app.get("/")
def root():
    return {"message": "Storely Alembic demo ishlamoqda."}


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

@app.get("/orders-columns", tags=["Debug"])
def check_order_columns(db: Session = Depends(get_db)):
    """orders jadvalidagi barcha ustunlarni ko'rsatish (PRAGMA orqali)."""
    result = db.execute(text("PRAGMA table_info(orders)"))
    columns = [{"name": row[1], "type": row[2]} for row in result]
    return {"columns": columns}

@app.post("/seed-demo-data", tags=["Debug"])
def seed_demo_data(db: Session = Depends(get_db)):
    customer = Customer(full_name="Aziz Karimov", phone="+998901234567")
    db.add(customer)
    db.commit()
    db.refresh(customer)

    order1 = Order(total_amount=150000, status="pending", customer_id=customer.id)
    order2 = Order(total_amount=320000, status="completed", customer_id=customer.id)
    db.add_all([order1, order2])
    db.commit()

    return {"customer": customer.full_name, "orders_added": 2}


@app.get("/customer-with-orders", tags=["Debug"])
def customer_with_orders(db: Session = Depends(get_db)):
    customer = db.query(Customer).first()
    if not customer:
        return {"message": "Hali mijoz yo'q. Avval /seed-demo-data ni chaqiring"}
    return {
        "customer": customer.full_name,
        "orders": [{"id": o.id, "total": o.total_amount, "status": o.status} for o in customer.orders],
    }


@app.get("/order-with-customer/{order_id}", tags=["Debug"])
def order_with_customer(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"message": "Bunday order topilmadi"}
    return {
        "order_id": order.id,
        "total_amount": order.total_amount,
        "customer_name": order.customer.full_name,
    }