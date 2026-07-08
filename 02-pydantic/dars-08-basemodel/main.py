"""
Dars 08 — Pydantic BaseModel
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Pydantic BaseModel demo", version="1.0.0")


# ---------- Pydantic modellar ----------
class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    in_stock: bool = True


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)


# ---------- In-memory "database" ----------
products_db: list[dict] = []
next_id = 1


# ---------- Endpointlar ----------
@app.post("/products", status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: Product):
    """
    Request body — Product modeliga mos JSON bo'lishi kerak.
    FastAPI avtomatik validatsiya qiladi.
    """
    global next_id
    new_product = {"id": next_id, **product.model_dump()}
    products_db.append(new_product)
    next_id += 1
    return new_product


@app.get("/products", tags=["Products"])
def list_products():
    return {"products": products_db}


@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Mahsulot topilmadi")


@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: int, product: ProductUpdate):
    for p in products_db:
        if p["id"] == product_id:
            p["name"] = product.name
            p["price"] = product.price
            return p
    raise HTTPException(status_code=404, detail="Mahsulot topilmadi")


# Ishga tushirish: uvicorn main:app --reload
#
# /docs orqali POST /products ni sinab ko'ring:
# {
#   "name": "Choynak",
#   "price": 25.5,
#   "in_stock": true
# }
#
# Keyin QASDDAN xato ma'lumot yuboring:
# {
#   "name": "C",
#   "price": -5
# }
# 422 xato va aniq qaysi maydon xato ekanini ko'rasiz