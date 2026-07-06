# Dars 06 — Path Parameters, Query Parameters, Validation

## 1. Path Parameter nima?

Path parameter — manzilning **o'zi ichida** keladigan qiymat, odatda
resursni aniqlash uchun ishlatiladi (masalan qaysi ID).

```python
@app.get("/books/{book_id}")
def get_book(book_id: int):
    return {"book_id": book_id}
```

`http://.../books/5` → `book_id = 5`

**Muhim:** FastAPI type hint (`book_id: int`) orqali avtomatik konvertatsiya
va validatsiya qiladi. Agar `http://.../books/abc` deb yuborsangiz,
FastAPI **avtomatik 422 xato** qaytaradi — buni qo'lda tekshirish shart
emas (Django DRF'da buni `int:` converter yoki serializer bilan qo'lda
qilgan bo'lardingiz).

## 2. Query Parameter nima?

Query parameter — manzildan keyin `?key=value` ko'rinishida keladigan
qo'shimcha parametrlar, odatda **filtrlash, saralash, pagination** uchun
ishlatiladi.

```python
@app.get("/books")
def list_books(available: bool = None, limit: int = 10):
    return {"available": available, "limit": limit}
```

`http://.../books?available=true&limit=5`

**Muhim farq path va query o'rtasida:**
- Path parameter — funksiya imzosida **path'dagi `{}`** ichida ko'rsatilgan bo'lsa
- Query parameter — path'da ko'rsatilmagan, lekin funksiya parametrida bo'lgan har qanday narsa **avtomatik** query parameter deb hisoblanadi

```python
@app.get("/books/{book_id}")
def get_book(book_id: int, lang: str = "uz"):
    # book_id — path parameter (path'da {book_id} bor)
    # lang — query parameter (path'da yo'q, lekin funksiyada bor)
    return {"book_id": book_id, "lang": lang}
```

`http://.../books/5?lang=en` → `book_id=5, lang="en"`

## 3. Majburiy vs ixtiyoriy parametrlar

```python
@app.get("/search")
def search(q: str, limit: int = 10, offset: int = 0):
    # q — MAJBURIY (default qiymat yo'q)
    # limit, offset — IXTIYORIY (default qiymat bor)
    return {"q": q, "limit": limit, "offset": offset}
```

Agar `q` berilmasa (`http://.../search`), FastAPI avtomatik **422** xato
qaytaradi: "field required".

## 4. `Optional` bilan ixtiyoriy, lekin default'siz parametr

```python
from typing import Optional

@app.get("/books")
def list_books(category: Optional[str] = None):
    if category:
        return {"filtered_by": category}
    return {"message": "barcha kitoblar"}
```

`Optional[str] = None` — parametr berilishi shart emas, berilmasa `None`
bo'ladi.

## 5. `Query()` va `Path()` — validatsiya qo'shish

FastAPI'da parametrlarga qo'shimcha validatsiya qoidalari qo'yish mumkin —
bu Django DRF'dagi serializer field validatorlariga o'xshaydi:

```python
from fastapi import FastAPI, Query, Path

app = FastAPI()

@app.get("/books")
def list_books(
    limit: int = Query(default=10, ge=1, le=100, description="Nechta natija qaytarish"),
    q: str = Query(default=None, min_length=3, max_length=50),
):
    return {"limit": limit, "q": q}


@app.get("/books/{book_id}")
def get_book(
    book_id: int = Path(..., ge=1, description="Kitob ID'si, 1 dan boshlab"),
):
    return {"book_id": book_id}
```

### Foydali validatsiya parametrlari

| Parametr | Ma'nosi | Misol |
|---|---|---|
| `ge` | greater than or equal (≥) | `ge=1` — 1 yoki undan katta |
| `le` | less than or equal (≤) | `le=100` — 100 yoki undan kichik |
| `gt` | greater than (>) | `gt=0` — 0 dan katta |
| `lt` | less than (<) | `lt=1000` |
| `min_length` | Minimal uzunlik (string) | `min_length=3` |
| `max_length` | Maksimal uzunlik (string) | `max_length=50` |
| `regex` / `pattern` | Regex bilan tekshirish | `pattern="^[a-z]+$"` |

**`...` (Ellipsis) nima?** — `Path(..., ge=1)` da `...` "bu parametr
**majburiy**" degani. Agar default qiymat berilmoqchi bo'lsa, `...`
o'rniga qiymatni yozasiz: `Query(10, ge=1)`.

## 6. Enum bilan cheklangan qiymatlar

Agar parametr faqat oldindan belgilangan qiymatlardan birini qabul
qilishi kerak bo'lsa (masalan status: faqat "active", "inactive",
"pending"), `Enum` ishlatiladi:

```python
from enum import Enum

class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"
    lost = "lost"


@app.get("/books/status/{status}")
def filter_by_status(status: BookStatus):
    return {"status": status}
```

Bu holatda Swagger UI'da avtomatik **dropdown** paydo bo'ladi — foydalanuvchi
faqat shu 3 variantdan birini tanlashi mumkin, boshqa qiymat yuborsa 422
xato oladi.

## 7. Ko'p qiymatli query parameter (list)

```python
from typing import List

@app.get("/books")
def filter_books(tags: List[str] = Query(default=[])):
    return {"tags": tags}
```

So'rov: `http://.../books?tags=fantastika&tags=drama`
Natija: `{"tags": ["fantastika", "drama"]}`

## 8. Path va Query'ni birga ishlatish (real misol)

```python
@app.get("/authors/{author_id}/books")
def get_author_books(
    author_id: int = Path(..., ge=1),
    published_after: Optional[int] = Query(default=None, description="Yil"),
    limit: int = Query(default=10, le=50),
):
    return {
        "author_id": author_id,
        "published_after": published_after,
        "limit": limit,
    }
```

`http://.../authors/3/books?published_after=2020&limit=5`

Bu naqsh sizning Delivery API loyihangizda juda ko'p ishlatiladi —
masalan `/customers/{customer_id}/orders?status=pending&limit=20`.

## Xulosa

- **Path parameter** — manzil ichida, resursni aniqlash uchun (`/books/{id}`)
- **Query parameter** — `?key=value`, filtrlash/pagination uchun
- `Query()` va `Path()` — validatsiya qoidalari qo'shish uchun (`ge`, `le`, `min_length` va h.k.)
- `Enum` — cheklangan qiymatlar to'plami uchun, Swagger'da dropdown beradi
- FastAPI validatsiyani **avtomatik** bajaradi — noto'g'ri qiymat kelsa,
  siz kod yozmasdan ham 422 xato qaytariladi