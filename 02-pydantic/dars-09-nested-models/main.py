"""
Dars 09 — Nested Models, List, Optional, EmailStr
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Nested Models demo", version="1.0.0")


# ---------- Nested Pydantic modellar ----------
class Address(BaseModel):
    city: str
    street: str
    zip_code: Optional[str] = None


class Customer(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    address: Optional[Address] = None


class OrderItem(BaseModel):
    product_name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class Order(BaseModel):
    customer: Customer
    items: List[OrderItem]

    def total_price(self) -> float:
        return sum(item.quantity * item.price for item in self.items)


# ---------- In-memory "database" ----------
orders_db: list[dict] = []
next_id = 1


# ---------- Endpointlar ----------
@app.post("/orders", status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order: Order):
    global next_id
    new_order = {
        "id": next_id,
        "customer": order.customer.model_dump(),
        "items": [item.model_dump() for item in order.items],
        "total_price": order.total_price(),
    }
    orders_db.append(new_order)
    next_id += 1
    return new_order


@app.get("/orders", tags=["Orders"])
def list_orders():
    return {"orders": orders_db}


@app.get("/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int):
    for o in orders_db:
        if o["id"] == order_id:
            return o
    raise HTTPException(status_code=404, detail="Buyurtma topilmadi")


# Ishga tushirish: uvicorn main:app --reload
#
# POST /orders uchun test JSON:
# {
#   "customer": {
#     "name": "Botir",
#     "email": "botir@example.com",
#     "address": {"city": "Tashkent", "street": "Chilonzor"}
#   },
#   "items": [
#     {"product_name": "Choynak", "quantity": 2, "price": 25.5},
#     {"product_name": "Piyola", "quantity": 6, "price": 5.0}
#   ]
# }
#
# Keyin xato email bilan sinang: "email": "botir-email-emas"
# → 422 xato, EmailStr avtomatik tekshiradi