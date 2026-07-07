"""
Dars 07 — Mustaqil mashq: Library System bilan Dependency Injection

Statik ma'lumot:
books = [
    {"id": 1, "title": "Alisa Mo'jizalar Mamlakatida", "borrowed": False},
    {"id": 2, "title": "Pinokkio", "borrowed": True},
    {"id": 3, "title": "Kichkina Shahzoda", "borrowed": False},
]

Vazifa:

1. `pagination_params(skip: int = 0, limit: int = 10)` funksiya-dependency
   yarating. Buni "/books" endpointida ishlating — natijani
   {"skip": ..., "limit": ..., "books": books[skip:skip+limit]} qilib
   qaytaring.

2. Class-based dependency yarating: `BookFilter`
   - __init__(self, borrowed: Optional[bool] = None)
   "/books/filter" endpointida ishlating — borrowed bo'yicha filtrlab
   qaytaring.

3. Nested dependency yarating:
   - `get_library_db()` — {"library": "Tashkent Central Library"} qaytarsin
   - `get_librarian(db: dict = Depends(get_library_db))` —
     {"librarian": "Aziza", "library": db["library"]} qaytarsin
   "/librarian-info" endpointida `get_librarian`ni ishlating.

4. `yield` bilan dependency yarating: `get_session()`
   - Session ochilganda: print(">> Session boshlandi")
   - Session yopilganda: print(">> Session tugadi")
   "/books/session-demo" endpointida ishlating, session ma'lumotini
   qaytaring.

5. Bonus: Header orqali oddiy autentifikatsiya dependency yarating:
   `verify_token(x_token: str = Header(...))` — agar x_token !=
   "kutubxona-tokeni" bo'lsa, HTTPException 401 qaytarsin.
   "/books/admin" endpointida ishlating — faqat to'g'ri token bilan
   kirish mumkin bo'lsin.
"""

from typing import Optional
from fastapi import FastAPI, Depends, Header, HTTPException, status

app = FastAPI(title="Library Dependency Injection", version="1.0.0")

books = [
    {"id": 1, "title": "Alisa Mo'jizalar Mamlakatida", "borrowed": False},
    {"id": 2, "title": "Pinokkio", "borrowed": True},
    {"id": 3, "title": "Kichkina Shahzoda", "borrowed": False},
]


# TODO: pagination_params funksiyasini yozing va "/books" da ishlating
def common_pagination(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/books", tags=["Library"])
def list_books(pagination: dict = Depends(common_pagination)):
    return {"books": books[pagination["skip"]:pagination["skip"] + pagination["limit"]], **pagination}  


# TODO: BookFilter klassini yozing va "/books/filter" da ishlating
class BookFilter:
    def __init__(self, borrowed: Optional[bool] = None):
        self.borrowed = borrowed

@app.get("/books/filter", tags=["Library"])
def filter_books(filter: BookFilter = Depends(BookFilter)):
    if filter.borrowed is None:
        return {"books": books}
    filtered_books = [book for book in books if book["borrowed"] == filter.borrowed]
    return {"books": filtered_books}


# TODO: get_library_db va get_librarian funksiyalarini yozing,
#       "/librarian-info" da ishlating
def get_library_db():
    return {"library": "Tashkent Central Library"}


def get_librarian(db: dict = Depends(get_library_db)):
    return {"librarian": "Aziza", "library": db["library"]}

@app.get("/librarian-info", tags=["Library"])
def librarian_info(librarian: dict = Depends(get_librarian)):
    return librarian



# TODO: get_session (yield bilan) funksiyasini yozing,
#       "/books/session-demo" da ishlating
def get_session():
    print(">> Session boshlandi")
    session = {"session_id": "session-123"}
    try:
        yield session
    finally:
        print(">> Session tugadi")

@app.get("/books/session-demo", tags=["Library"])
def session_demo(session: dict = Depends(get_session)):
    return session


# TODO (bonus): verify_token funksiyasini yozing,
#       "/books/admin" da ishlating
def verify_token(x_token: str = Header(...)):
    if x_token != "kutubxona-tokeni":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri token",
        )
    return x_token
    
@app.get("/books/admin", tags=["Library"])
def admin_books(token: str = Depends(verify_token)):
    return {"books": books, "message": "Admin access granted"}
