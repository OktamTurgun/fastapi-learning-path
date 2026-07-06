"""
Dars 06 — Path Parameters, Query Parameters, Validation
"""

from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, Query, Path

app = FastAPI(
    title="Path & Query Params demo",
    version="1.0.0",
)

books = [
    {"id": 1, "title": "Alisa Mo'jizalar Mamlakatida", "status": "available", "year": 1865},
    {"id": 2, "title": "Pinokkio", "status": "borrowed", "year": 1883},
    {"id": 3, "title": "Kichkina Shahzoda", "status": "available", "year": 1943},
]


class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"
    lost = "lost"


# ---------- Path parameter + validatsiya ----------
@app.get("/books/{book_id}", tags=["Books"])
def get_book(
    book_id: int = Path(..., ge=1, description="Kitob ID'si, 1 dan boshlab"),
):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"xato": "Kitob topilmadi"}


# ---------- Query parameter + validatsiya ----------
@app.get("/books", tags=["Books"])
def list_books(
    status: Optional[BookStatus] = Query(default=None, description="Holat bo'yicha filtr"),
    year_after: Optional[int] = Query(default=None, ge=0, description="Shu yildan keyin nashr etilganlar"),
    limit: int = Query(default=10, ge=1, le=100, description="Nechta natija"),
):
    result = books

    if status:
        result = [b for b in result if b["status"] == status]

    if year_after:
        result = [b for b in result if b["year"] > year_after]

    return {"count": len(result), "books": result[:limit]}


# ---------- Ko'p qiymatli query parameter ----------
@app.get("/books/search/by-ids", tags=["Books"])
def search_by_ids(ids: List[int] = Query(default=[])):
    result = [b for b in books if b["id"] in ids]
    return {"books": result}


# ---------- Path + Query birga ----------
@app.get("/authors/{author_id}/books", tags=["Authors"])
def author_books(
    author_id: int = Path(..., ge=1),
    limit: int = Query(default=5, le=20),
):
    # Demo maqsadida — haqiqiy author-book bog'lanishi Dars 13'da (Relationships)
    return {"author_id": author_id, "limit": limit, "books": books[:limit]}


# Ishga tushirish: uvicorn main:app --reload
#
# Sinab ko'ring:
# http://127.0.0.1:8000/books/1
# http://127.0.0.1:8000/books/abc          <- 422 xato (int emas)
# http://127.0.0.1:8000/books?status=available
# http://127.0.0.1:8000/books?year_after=1900&limit=1
# http://127.0.0.1:8000/books/search/by-ids?ids=1&ids=3
# http://127.0.0.1:8000/docs               <- status uchun dropdown ko'ring