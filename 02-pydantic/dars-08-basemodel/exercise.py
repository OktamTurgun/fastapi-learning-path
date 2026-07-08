"""
Dars 08 — Mustaqil mashq: Storely Product API (Pydantic bilan)

Vazifa:

1. `Product` Pydantic modelini yarating:
   - name: str, min_length=2, max_length=100 (majburiy)
   - price: float, gt=0 (majburiy)
   - category: str (majburiy)
   - quantity: int, ge=0, default=0 (ixtiyoriy)
   - description: Optional[str] = None (ixtiyoriy)

2. `ProductUpdate` Pydantic modelini yarating (PUT uchun):
   - name: str, min_length=2, max_length=100
   - price: float, gt=0
   - quantity: int, ge=0

3. In-memory `products_db: list = []` va `next_id = 1` yarating.

4. POST "/products" — Product modelini qabul qilib, yangi mahsulot
   qo'shsin, status_code=201.

5. GET "/products" — barcha mahsulotlarni qaytarsin.

6. GET "/products/{product_id}" — bitta mahsulotni qaytarsin,
   topilmasa HTTPException 404.

7. PUT "/products/{product_id}" — ProductUpdate bilan to'liq yangilasin,
   topilmasa HTTPException 404.

8. Bonus: Product modeliga `total_value()` metodini qo'shing —
   `price * quantity` ni qaytarsin. Buni GET /products/{id} javobida
   qo'shimcha maydon sifatida ko'rsating (masalan
   {"id": ..., "name": ..., ..., "total_value": ...}).

Test uchun JSON:
{
  "name": "Simli sichqoncha",
  "price": 45000,
  "category": "electronics",
  "quantity": 15
}
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Storely Product API", version="1.0.0")


class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    quantity: int = Field(default=0, ge=0)
    description: Optional[str] = None

    def total_value(self) -> float:
        return self.price * self.quantity


class ProductUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


products_db: list[dict] = []
next_id = 1


@app.post("/products", status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: Product):
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
            product = Product(**p)
            return {**p, "total_value": product.total_value()}
    raise HTTPException(status_code=404, detail="Maxsulot topilmadi!")


@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: int, product: ProductUpdate):
    for p in products_db:
        if p["id"] == product_id:
            p["name"] = product.name
            p["price"] = product.price
            p["quantity"] = product.quantity
            return p
    raise HTTPException(status_code=404, detail="Maxsulot topilmadi!")
  