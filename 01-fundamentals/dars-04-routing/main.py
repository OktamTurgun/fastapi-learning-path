"""
Dars 04 — Routing
Asosiy fayl endi faqat routerlarni yig'ish vazifasini bajaradi —
biznes-logika routers/ ichidagi fayllarda joylashgan.
"""

from fastapi import FastAPI
from routers import users, products

app = FastAPI(
    title="Routing demo",
    description="APIRouter, include_router, tags va prefix bilan tanishuv",
    version="1.0.0",
)

# Har bir routerni o'z prefix va tag'i bilan ulaymiz
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])


@app.get("/", tags=["Root"])
def root():
    return {"message": "Routing demo API ishlamoqda"}


# Ishga tushirish: uvicorn main:app --reload
#
# Sinab ko'ring:
# http://127.0.0.1:8000/users/
# http://127.0.0.1:8000/users/1
# http://127.0.0.1:8000/products/
# http://127.0.0.1:8000/products/2
# http://127.0.0.1:8000/docs   <- "Users" va "Products" guruhlarini ko'ring