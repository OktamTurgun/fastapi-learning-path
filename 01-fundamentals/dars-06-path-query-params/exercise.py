"""
Dars 06 — Mustaqil mashq: Product Catalog API

Statik ma'lumot:
products = [
    {"id": 1, "name": "Choynak", "category": "kitchen", "price": 25.50, "in_stock": True},
    {"id": 2, "name": "Piyola", "category": "kitchen", "price": 5.00, "in_stock": True},
    {"id": 3, "name": "Stol", "category": "furniture", "price": 450.00, "in_stock": False},
    {"id": 4, "name": "Stul", "category": "furniture", "price": 120.00, "in_stock": True},
]

Vazifa:

1. GET "/products/{product_id}" — Path(..., ge=1) bilan validatsiya qiling.
   Topilmasa {"xato": "Mahsulot topilmadi"} qaytaring.

2. Enum yarating — ProductCategory("kitchen", "furniture", "electronics").

3. GET "/products" — quyidagi query parametrlar bilan:
   - category: Optional[ProductCategory] = None  (filtrlash uchun)
   - min_price: Optional[float] = Query(default=None, ge=0)
   - max_price: Optional[float] = Query(default=None, ge=0)
   - in_stock: Optional[bool] = None
   - limit: int = Query(default=10, ge=1, le=50)

   Barcha berilgan filtrlarni qo'llab, natijani qaytaring.
   (Masalan: faqat category berilsa — shu categorydagilarni,
   min_price VA max_price berilsa — shu oraliqdagilarni qaytaring)

4. Bonus: GET "/products/search/by-ids" — List[int] query parameter
   bilan bir nechta id orqali mahsulotlarni qaytaring.

Test qilish uchun manzillar (yozib qo'ying, keyin sinaysiz):
- /products?category=kitchen
- /products?min_price=50&max_price=500
- /products?in_stock=true&limit=2
- /products/abc          <- 422 xato kutilmoqda
- /products/0            <- 422 xato kutilmoqda (ge=1 buzilgani uchun)
"""

from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, Query, Path, HTTPException, status

app = FastAPI(title="Product Catalog API", version="1.0.0")

products = [
    {"id": 1, "name": "Choynak", "category": "kitchen", "price": 25.50, "in_stock": True},
    {"id": 2, "name": "Piyola", "category": "kitchen", "price": 5.00, "in_stock": True},
    {"id": 3, "name": "Stol", "category": "furniture", "price": 450.00, "in_stock": False},
    {"id": 4, "name": "Stul", "category": "furniture", "price": 120.00, "in_stock": True},
]


# TODO: ProductCategory Enum yarating (kitchen, furniture, electronics)
class ProductCategory(str, Enum):
    kitchen = "kitchen"
    furniture = "furniture"
    electronics = "electronics"


@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int = Path(..., ge=1)):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")
    return product

# TODO: GET "/products" — barcha filtr query parametrlari bilan
@app.get("/products", tags=["Products"])
def list_products(
    category: Optional[ProductCategory] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    in_stock: Optional[bool] = None,
    limit: int = Query(default=10, ge=1, le=50),
):
    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"count": len(result), "products": result[:limit]}


# TODO (bonus): GET "/products/search/by-ids" — List[int] bilan
@app.get("/products/search/by-ids", tags=["Products"])
def search_products_by_ids(ids: List[int] = Query(default=[])):
    result = [p for p in products if p["id"] in ids]
    return {"products": result}
