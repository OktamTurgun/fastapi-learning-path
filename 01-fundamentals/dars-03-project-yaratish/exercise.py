"""
Dars 03 — Mustaqil mashq

Vazifa:
1. Yangi FastAPI ilova yarating, quyidagi metadata bilan:
   - title: "Storely API" (yoki xohlagan loyihangiz nomi)
   - description: qisqacha loyiha tavsifi
   - version: "1.0.0"

2. "/" manzilida root endpoint yarating, tags=["Root"] bilan,
   {"status": "ok"} qaytarsin.

3. "/products" manzilida endpoint yarating, tags=["Products"] bilan,
   3 ta statik mahsulot ro'yxatini JSON qilib qaytaring
   (masalan: id, name, price maydonlari bilan).

4. Serverni quyidagi flag'lar bilan ishga tushiring:
   uvicorn exercise:app --reload --host 0.0.0.0 --port 8001

5. /docs sahifasini oching va endpointlar "Root" va "Products"
   guruhlariga qanday ajralganini kuzating.

Bonus (ixtiyoriy):
6. /openapi.json ni brauzerda oching va u yerda title, version
   qanday aks etganini toping.
"""

from fastapi import FastAPI

# TODO: FastAPI() ni title, description, version bilan sozlang
app = FastAPI(
    title="Storely API",
    description="Storely replaces the notebook with an intelligent system accessible via Telegram — no app installation required",
    version="1.0.0",
    contact={"name": "github", "url": "https://github.com/OktamTurgun"},
)


# TODO: "/" endpointini tags=["Root"] bilan yozing
@app.get("/", tags=["Root"])
def root():
    """Ildiz endpoint - Storely API ishlab turganini tekshirish uchun."""
    return {"status": "ok", "message": "Storely API ishlamoqda."}


# TODO: "/products" endpointini tags=["Products"] bilan yozing
@app.get("/products", tags=["Products"])
def products():
    """products endpointi - barcha productlar listini qaytaradi."""
    return {
        "products": [
            {"id": "1", "name": "magic_car", "price": 45.00},
            {"id": "2", "name": "Batman", "price": 33.99},
            {"id": "3", "name": "bear", "price": 12.99},
        ]
    }
