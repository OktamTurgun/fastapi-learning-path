"""
Products bilan bog'liq barcha endpointlar.
"""

from fastapi import APIRouter

router = APIRouter()

fake_products = [
    {"id": 1, "name": "Choynak", "price": 25.50},
    {"id": 2, "name": "Piyola", "price": 5.00},
]


@router.get("/")
def list_products():
    """Barcha mahsulotlar ro'yxati."""
    return {"products": fake_products}


@router.get("/{product_id}")
def get_product(product_id: int):
    """Bitta mahsulotni id orqali topish."""
    for product in fake_products:
        if product["id"] == product_id:
            return product
    return {"xato": "Mahsulot topilmadi"}