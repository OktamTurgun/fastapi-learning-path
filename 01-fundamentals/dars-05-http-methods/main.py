"""
Dars 05 — HTTP Methods
To'liq CRUD amallari — hozircha statik (in-memory) ro'yxat bilan.
Dars 15'da bu haqiqiy database bilan almashtiriladi.
"""

from fastapi import FastAPI, HTTPException, status

app = FastAPI(
    title="HTTP Methods demo",
    description="GET, POST, PUT, PATCH, DELETE va status kodlar",
    version="1.0.0",
)

# In-memory "database" — server qayta ishga tushsa, ma'lumot yo'qoladi
books = [
    {"id": 1, "title": "Alisa Mo'jizalar Mamlakatida", "available": True},
    {"id": 2, "title": "Pinokkio", "available": False},
]


# ---------- GET ----------
@app.get("/books", tags=["Books"])
def list_books():
    """Barcha kitoblar ro'yxati."""
    return {"books": books}


@app.get("/books/{book_id}", tags=["Books"])
def get_book(book_id: int):
    """Bitta kitobni id orqali topish. Topilmasa 404 qaytaradi."""
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Kitob (id={book_id}) topilmadi",
    )


# ---------- POST ----------
@app.post("/books", status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(title: str, available: bool = True):
    """Yangi kitob qo'shish. Muvaffaqiyatli bo'lsa 201 qaytaradi."""
    new_id = max((b["id"] for b in books), default=0) + 1
    new_book = {"id": new_id, "title": title, "available": available}
    books.append(new_book)
    return new_book


# ---------- PUT ----------
@app.put("/books/{book_id}", tags=["Books"])
def replace_book(book_id: int, title: str, available: bool):
    """
    Kitobni TO'LIQ almashtiradi — shuning uchun PUT'da
    barcha maydonlar (title VA available) majburiy.
    """
    for book in books:
        if book["id"] == book_id:
            book["title"] = title
            book["available"] = available
            return book
    raise HTTPException(status_code=404, detail="Kitob topilmadi")


# ---------- PATCH ----------
@app.patch("/books/{book_id}", tags=["Books"])
def update_book(book_id: int, available: bool):
    """
    Kitobni QISMAN yangilaydi — faqat 'available' maydonini
    o'zgartiradi, 'title' o'zgarishsiz qoladi.
    """
    for book in books:
        if book["id"] == book_id:
            book["available"] = available
            return book
    raise HTTPException(status_code=404, detail="Kitob topilmadi")


# ---------- DELETE ----------
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int):
    """Kitobni ro'yxatdan o'chiradi. Muvaffaqiyatli bo'lsa body qaytmaydi (204)."""
    for i, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Kitob topilmadi")


# Ishga tushirish: uvicorn main:app --reload
#
# /docs orqali sinab ko'ring — har bir method rangi bilan ajratilgan
# (GET=ko'k, POST=yashil, PUT=to'q sariq, DELETE=qizil)