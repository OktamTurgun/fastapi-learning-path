"""
Dars 10 — Response Model, Alias, Config, Serializer
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field

app = FastAPI(title="Response Model demo", version="1.0.0")


# ---------- Request va Response uchun ALOHIDA modellar ----------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    # DIQQAT: password bu yerda yo'q — hech qachon clientga qaytmaydi


# ---------- Alias bilan model ----------
class ProductResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str = Field(..., alias="productName")
    price: float
    quantity: int

    @computed_field
    @property
    def total_value(self) -> float:
        return round(self.price * self.quantity, 2)


# ---------- In-memory "database" ----------
users_db: list[dict] = []
next_user_id = 1

products_db = [
    {"id": 1, "name": "Choynak", "price": 25.5, "quantity": 10},
]


# ---------- Endpointlar ----------
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate):
    """
    E'tibor bering: funksiya to'liq dict (password bilan) qaytaradi,
    lekin response_model=UserResponse tufayli password clientga
    yuborilmaydi — FastAPI avtomatik filtrlaydi.
    """
    global next_user_id
    new_user = {
        "id": next_user_id,
        "username": user.username,
        "email": user.email,
        "password": f"hashed_{user.password}",  # real loyihada bcrypt bilan hash qilinadi
    }
    users_db.append(new_user)
    next_user_id += 1
    return new_user   # to'liq dict qaytaramiz, lekin password chiqmaydi!


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Mahsulot topilmadi")


# Ishga tushirish: python -m uvicorn main:app --reload
#
# POST /users bilan sinang:
# {
#   "username": "uktam",
#   "email": "uktam@example.com",
#   "password": "maxfiy123"
# }
# Javobda "password" YO'QLIGINI tasdiqlang!
#
# GET /products/1 — javobda "productName" (alias) va "total_value"
# (computed_field) ko'rinishini tekshiring