"""
Dars 04 — Mustaqil mashq: Main

Vazifa:
1. FastAPI() ilovasini yarating (title, description, version bilan).
2. orders.router'ni prefix="/orders", tags=["Orders"] bilan ulang.
3. "/" manzilida root endpoint yarating.
"""

from fastapi import FastAPI

# TODO: routers papkasidan orders'ni import qiling
from routers import orders

# TODO: FastAPI() yarating
app = FastAPI(
    title="Routing demo",
    description="APIRouter, include_router, tags va prefix bilan tanishuv",
    version="1.0.0",
)


# TODO: orders.router'ni include_router() bilan ulang
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

# TODO: "/" root endpointini yozing
@app.get("/", tags=["Root"])
def root():
    return {"message": "Routing demo API ishlamoqda!"}

# Ishga tushirish: uvicorn main:app --reload
#
# Sinab ko'ring:
# http://127.0.0.1:8000/orders/
# http://127.0.0.1:8000/orders/1/
# http://127.0.0.1:8000/docs   <- "Orders" guruhlarini ko'ring