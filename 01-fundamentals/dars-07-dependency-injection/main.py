"""
Dars 07 — Dependency Injection
"""

from fastapi import FastAPI, Depends, Header, HTTPException, status

app = FastAPI(title="Dependency Injection demo", version="1.0.0")


# ---------- 1. Oddiy funksiya-dependency ----------
def common_pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/products", tags=["Demo"])
def list_products(pagination: dict = Depends(common_pagination)):
    return {"resource": "products", **pagination}


@app.get("/orders", tags=["Demo"])
def list_orders(pagination: dict = Depends(common_pagination)):
    return {"resource": "orders", **pagination}


# ---------- 2. Class-based dependency ----------
class CommonParams:
    def __init__(self, skip: int = 0, limit: int = 10, q: str = None):
        self.skip = skip
        self.limit = limit
        self.q = q


@app.get("/search", tags=["Demo"])
def search(params: CommonParams = Depends(CommonParams)):
    return {"skip": params.skip, "limit": params.limit, "q": params.q}


# ---------- 3. Nested dependency (dependency ichida dependency) ----------
def get_db():
    """Demo — haqiqiy DB Dars 12'da qo'shiladi."""
    return {"connection": "fake_db_connection_active"}


def get_current_user(db: dict = Depends(get_db)):
    """DB orqali (hozircha demo) foydalanuvchini olib kelish."""
    return {"id": 1, "ism": "Uktam", "db_status": db["connection"]}


@app.get("/profile", tags=["Demo"])
def read_profile(user: dict = Depends(get_current_user)):
    return user


# ---------- 4. yield bilan dependency (setup/cleanup) ----------
def get_db_session():
    print(">> DB session ochildi")
    session = {"session_id": "abc-123"}
    try:
        yield session
    finally:
        print(">> DB session yopildi")


@app.get("/orders-with-session", tags=["Demo"])
def orders_with_session(session: dict = Depends(get_db_session)):
    return {"session_id": session["session_id"], "orders": ["order1", "order2"]}


# ---------- 5. Dependency orqali autentifikatsiya (soddalashtirilgan) ----------
def verify_api_key(x_api_key: str = Header(...)):
    """
    Header orqali API key tekshirish (demo).
    Haqiqiy so'rovda header nomi 'X-API-Key' bo'lishi kerak.
    """
    if x_api_key != "maxfiy-kalit-123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri API key",
        )
    return x_api_key


@app.get("/secure-data", tags=["Demo"])
def secure_data(api_key: str = Depends(verify_api_key)):
    return {"message": "Maxfiy ma'lumot", "api_key_used": api_key}


# Ishga tushirish: uvicorn main:app --reload
#
# Sinab ko'ring:
# http://127.0.0.1:8000/products?skip=5&limit=20
# http://127.0.0.1:8000/search?q=fastapi
# http://127.0.0.1:8000/profile
# http://127.0.0.1:8000/orders-with-session   <- terminalda print'larni kuzating
#
# /secure-data uchun Header kerak — buni faqat /docs orqali yoki
# curl bilan sinab ko'rish mumkin:
# curl -H "X-API-Key: maxfiy-kalit-123" http://127.0.0.1:8000/secure-data
# curl -H "X-API-Key: xato-kalit" http://127.0.0.1:8000/secure-data   <- 401 kutilmoqda