# Dars 16 — Pagination & Filtering (Storely)

Dars 15'da `skip`/`limit` bilan oddiy pagination yozgan edik. Endi buni
**real production darajasiga** ko'taramiz: qidiruv, saralash, filtrlash va
**umumiy son** bilan birga qaytariladigan pagination javobini yaratamiz.

## 1. Nega oddiy `skip`/`limit` yetarli emas?

Hozirgi holat:

```python
@router.get("/", response_model=list[ProductResponse])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_product.get_products(db, skip=skip, limit=limit)
```

### Muammolar

- Frontend **jami nechta yozuv borligini** bilmaydi. Masalan, UI-da
  "128 tadan 1-10 ko'rsatilmoqda" deb ko'rsatish uchun kerak bo'ladi.
- Qidiruv yo'q — mahsulot nomi bo'yicha izlash mumkin emas.
- Filtrlash yo'q — faqat bitta kategoriyadagi mahsulotlarni ko'rish mumkin emas.
- Saralash yo'q — narx yoki nom bo'yicha tartiblash imkoni yo'q.

> Django DRF bilan taqqoslaganda bu — `django-filter` + `PageNumberPagination`
yoki `LimitOffsetPagination`ning FastAPI-dagi qo'lda yozilgan ekvivalenti.

## 2. Umumiy sonli (`total count`) pagination response

```python
# schemas/product.py ichiga qo'shiladi
class PaginatedProducts(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ProductResponse]
```

Amaliyotda ko'pincha **har bir resurs uchun alohida** pagination schema yozish
soddaroq bo'ladi. Generic `TypeVar` ishlatish murakkabroq bo'lishi mumkin,
lekin katta loyihalarda foydali bo'lishi mumkin. Biz esa sodda yo'lni tanlaymiz:
har bir resurs uchun alohida `Paginated{Resource}` klassi.

## 3. `crud/product.py` — filtrlash, qidiruv va saralash bilan

```python
from sqlalchemy.orm import Session
from app.models.product import Product

ALLOWED_SORT_FIELDS = {"id", "name", "price", "quantity"}


def get_products_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> tuple[list[Product], int]:
    query = db.query(Product)

    # --- Qidiruv (nom bo'yicha, katta-kichik harf farqisiz) ---
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # --- Filtrlash ---
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # --- Umumiy son (filtrlangandan KEYIN, lekin limit/skip'dan OLDIN) ---
    total = query.count()

    # --- Saralash (xavfsiz — faqat ruxsat etilgan ustunlar) ---
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "id"
    sort_column = getattr(Product, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # --- Pagination ---
    items = query.offset(skip).limit(limit).all()

    return items, total
```

> **Muhim:** `total = query.count()` qiymati **filtrlashdan keyin**, lekin
> **`offset`/`limit`dan oldin** hisoblanishi kerak. Aks holda jami son noto'g'ri
> chiqadi — faqat joriy sahifadagi yozuvlar soni ko'rsatiladi.

## 4. Router — yangi query parametrlar bilan

```python
# app/routers/product.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import PaginatedProducts
from app.crud import product as crud_product

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedProducts)
def read_products(
    skip: int = Query(0, ge=0, description="Nechta yozuvni o'tkazib yuborish"),
    limit: int = Query(10, ge=1, le=100, description="Nechta yozuv qaytarish"),
    search: str | None = Query(None, description="Mahsulot nomi bo'yicha qidiruv"),
    category_id: int | None = Query(None, description="Kategoriya bo'yicha filtr"),
    min_price: float | None = Query(None, ge=0, description="Minimal narx"),
    max_price: float | None = Query(None, ge=0, description="Maksimal narx"),
    sort_by: str = Query("id", description="Saralash ustuni: id, name, price"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="asc yoki desc"),
    db: Session = Depends(get_db),
):
    items, total = crud_product.get_products_filtered(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )
    return PaginatedProducts(total=total, skip=skip, limit=limit, items=items)
```

### `Query(...)` nima uchun kerak?

Bu — FastAPI'ga query parametr uchun validatsiya qo'shish imkonini beradi:

- `ge=0` — manfiy son kiritilmasin.
- `le=100` — bir martada 100 tadan ortiq yozuv so'ralmasin.
- `pattern="^(asc|desc)$"` — faqat `asc` yoki `desc` qiymatlari qabul qilinsin.
- `description=...` — Swagger UI'da avtomatik ko'rinadi.

## 5. Sinash misollari

```http
GET /products/?search=simli
GET /products/?category_id=1
GET /products/?min_price=10000&max_price=100000
GET /products/?sort_by=price&order=desc
GET /products/?skip=0&limit=5&sort_by=name&order=asc
```

Hammasini birga:

```http
GET /products/?search=quloqchin&category_id=1&min_price=20000&sort_by=price&order=desc&skip=0&limit=5
```

## 6. Xavfsizlik eslatmasi — SQL Injection haqida

`sort_by` parametri **to'g'ridan-to'g'ri** ustun nomiga aylantirilmoqda
(`getattr(Product, sort_by, ...)`). Bu — SQL injection'ga ochiq **emas**,
chunki SQLAlchemy ORM ustun darajasida ishlaydi va xom SQL bo'lib qolmaydi.
Ammo agar foydalanuvchi mavjud bo'lmagan ustun nomini yuborsa, misol uchun
`sort_by=password`, bu xatoga olib kelishi mumkin.

### Shuning uchun

Biz `ALLOWED_SORT_FIELDS` — ruxsat etilgan ustunlar ro'yxatini oldindan
tekshiramiz:

```python
ALLOWED_SORT_FIELDS = {"id", "name", "price", "quantity"}

if sort_by not in ALLOWED_SORT_FIELDS:
    sort_by = "id"
```

Bu — Django DRF'dagi `ordering_fields = [...]` bilan bir xil g'oya.

## Xulosa

- **`total`** — filtrlashdan keyin, `offset`/`limit`dan oldin hisoblanadi.
- **`Query(...)`** — validatsiya (`ge`, `le`, `pattern`) qo'shish uchun ishlatiladi.
- **`ilike`** — katta-kichik harf farqisiz qidiruv uchun ishlatiladi.
- **`ALLOWED_SORT_FIELDS`** — xavfsiz saralash uchun oq ro'yxat (whitelist).
- **`PaginatedProducts`** — `total`, `skip`, `limit` va `items` bilan birga
  qaytariladigan standart shakl.

## ✍️ Mustaqil mashq

`exercise/` papkasida — `Order` uchun xuddi shunday filtrlash qo'shiladi:

- `status` bo'yicha filtr (`pending`, `completed` va h.k.)
- `min_amount`/`max_amount` — `total_amount` oralig'i bo'yicha
- `sort_by`: `id`, `total_amount`, `status`
- `PaginatedOrders` schema