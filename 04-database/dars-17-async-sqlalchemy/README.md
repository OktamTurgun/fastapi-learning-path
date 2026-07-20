# Dars 17 — Async SQLAlchemy (Storely)

Dars 02'da ASGI/WSGI farqini o'rgangan edingiz. Bu dars — o'sha
nazariyani **amalda** ko'rish: `def` o'rniga `async def`, `Session`
o'rniga `AsyncSession` ishlatamiz.

## 1. Nega bu muhim? (Django bilan solishtirib)

Django (WSGI, an'anaviy) — **har bir so'rov uchun bitta thread** band
qiladi. Agar DB so'rovi 200ms desa, o'sha thread 200ms davomida **hech
narsa qila olmaydi**, faqat kutadi.

FastAPI (ASGI, async) — DB so'rovi ketayotganda, **bitta event loop**
boshqa so'rovlarni parallel qayta ishlashi mumkin. Bu ayniqsa **I/O-bound**
operatsiyalar (DB, tashqi API, fayl o'qish) ko'p bo'lgan holatlarda katta
farq qiladi.

**MUHIM TUSHUNCHA:** Agar sizning endpointingiz `def` (sinxron) bo'lib,
lekin ichida sinxron `Session.query()` ishlatilsa — FastAPI buni **alohida
threadpool**da ishga tushiradi (Dars 15-16'da qilganimiz aynan shu). Bu ham
ishlaydi, lekin **chinakam asinxronlik emas** — haqiqiy yutuq faqat
`async def` + `AsyncSession` + async drayver birga ishlatilganda keladi.

| | Sinxron (`def` + `Session`) | Asinxron (`async def` + `AsyncSession`) |
|---|---|---|
| DB drayver | `psycopg2`, oddiy `sqlite3` | `asyncpg`, `aiosqlite` |
| Engine | `create_engine()` | `create_async_engine()` |
| Session | `Session` | `AsyncSession` |
| So'rov | `db.query(...).all()` | `await db.execute(select(...))` |
| Router | `def endpoint(...)` | `async def endpoint(...)` |

## 2. O'rnatish

SQLite uchun asinxron drayver — `aiosqlite`:

```powershell
pip install aiosqlite sqlalchemy[asyncio]
```

`requirements.txt`ga qo'shing:

```txt
aiosqlite==0.20.0
```
**Eslatma:** Productionda (PostgreSQL) `asyncpg` ishlatiladi — bu SQLite'nikidan
ancha tezroq va to'liq asinxron. Storely'ni kelajakda Render/Railway'ga
deploy qilganda, `postgresql+asyncpg://...` connection string ishlatiladi.

## 3. `database.py` — asinxron versiyaga o'tish

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# MUHIM: "sqlite:///" emas, "sqlite+aiosqlite:///" — drayver nomi ko'rsatilishi shart
DATABASE_URL = "sqlite+aiosqlite:///./storely.db"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

**E'tibor bering:**
- `create_engine` → `create_async_engine`
- `sessionmaker` → `async_sessionmaker`
- `sqlite:///` → `sqlite+aiosqlite:///` (drayver prefiksi qo'shildi)
- `expire_on_commit=False` — commit'dan keyin obyekt atributlariga
  qayta murojaat qilganda, avtomatik yangi so'rov yubormaslik uchun
  (async holatda bu **muhim**, chunki obyektga sinxron tarzda
  murojaat qilib bo'lmaydi)
- `get_db()` endi **`async def`** va `async with` ishlatadi

## 4. Alembic'ni ham asinxron qilish kerakmi?

**Yo'q, shart emas!** Alembic — migratsiyalarni **bir martalik**
skript sifatida ishga tushiradi, u parallel so'rovlarga muhtoj emas.
`alembic/env.py`da sinxron `engine_from_config` qoldirilishi mumkin,
faqat `sqlalchemy.url`da ham `sqlite+aiosqlite:///` yozish kifoya
(Alembic buni ichida to'g'ri boshqaradi) — yoki xohlasangiz, alohida
sinxron drayver (`sqlite:///`) bilan ham ishlatavering, ikkalasi ham
bir xil DB faylga yozadi.

Bu loyihada soddalik uchun **Alembic — sinxron holicha qoldiriladi**,
faqat ilova (`app/`) qismi asinxron bo'ladi.

## 5. CRUD funksiyalari — `async`/`await` bilan

Eng katta farq shu yerda: `db.query(...)` **endi ishlamaydi** —
`AsyncSession` da `.query()` metodi yo'q. Buning o'rniga SQLAlchemy
2.0 uslubidagi `select()` ishlatiladi:

```python
# crud/product.py (async versiya)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

ALLOWED_SORT_FIELDS = {"id", "name", "price", "quantity"}


async def get_product(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_products_filtered(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    category_id: int | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> tuple[list[Product], int]:
    query = select(Product)

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    # Umumiy sonni hisoblash — alohida so'rov kerak (async'da .count() yo'q)
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "id"
    sort_column = getattr(Product, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column).offset(skip).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return list(items), total


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate) -> Product | None:
    db_product = await get_product(db, product_id)
    if not db_product:
        return None

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    db_product = await get_product(db, product_id)
    if not db_product:
        return False

    await db.delete(db_product)
    await db.commit()
    return True
```

**Muhim farqlar (Dars 15-16'dagi sinxron versiyadan):**

| Sinxron | Asinxron |
|---|---|
| `db.query(Product).filter(...).first()` | `await db.execute(select(Product).where(...))` + `.scalar_one_or_none()` |
| `query.count()` | alohida `select(func.count())` so'rovi |
| `db.commit()` | `await db.commit()` |
| `db.refresh(obj)` | `await db.refresh(obj)` |
| `db.delete(obj)` | `await db.delete(obj)` |

## 6. Router — `async def` bilan

```python
# app/routers/product.py (async versiya)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, PaginatedProducts
from app.crud import product as crud_product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await crud_product.create_product(db, product)


@router.get("/", response_model=PaginatedProducts)
async def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    category_id: int | None = Query(None),
    sort_by: str = Query("id"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud_product.get_products_filtered(
        db, skip=skip, limit=limit, search=search,
        category_id=category_id, sort_by=sort_by, order=order,
    )
    return PaginatedProducts(total=total, skip=skip, limit=limit, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await crud_product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    db_product = await crud_product.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_product.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
```

**Muhim qoida:** Agar router `async def` bo'lsa, uning ichida chaqirilgan
**hamma** funksiya ham `async` bo'lishi va `await` bilan chaqirilishi
kerak — aks holda `coroutine was never awaited` degan ogohlantirish
yoki xato chiqadi.

## 7. `relationship()` bilan ishlashda muhim tuzoq — `lazy loading`

Sinxron holatda, `product.category.name` deb yozganingizda, SQLAlchemy
avtomatik qo'shimcha so'rov yuboradi (**lazy loading**). Async holatda
bu **ishlamaydi** — chunki lazy loading sinxron I/O talab qiladi, siz
esa `await` qilmagansiz.

**Yechim — `selectinload` bilan oldindan yuklash (eager loading):**

```python
from sqlalchemy.orm import selectinload

async def get_product_with_category(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category))   # <- category oldindan yuklanadi
        .where(Product.id == product_id)
    )
    return result.scalar_one_or_none()
```

Bizning `OrderResponse`dagi nested `CustomerResponse` misolida ham,
async'ga o'tganda **albatta** `selectinload(Order.customer)` qo'shish
kerak bo'ladi — aks holda `MissingGreenlet` degan xato chiqadi.

## Xulosa

- **`async def` + `AsyncSession` + `aiosqlite`/`asyncpg`** — chinakam
  asinxron DB ishlash uchun uchalasi ham birga kerak
- **`db.query()` yo'q** — `select()` + `await db.execute()` ishlatiladi
- **`.count()` yo'q** — alohida `select(func.count())` so'rovi kerak
- **`selectinload()`** — `relationship()`larni async holatda oldindan
  yuklash uchun **majburiy** (aks holda `MissingGreenlet` xatosi)
- **Alembic** — sinxron holicha qoldirilishi mumkin, chunki u
  bir martalik skript, parallel so'rovlarga muhtoj emas