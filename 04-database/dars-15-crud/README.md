# Dars 15 — CRUD (Storely)

Dars 13-14'da modellar va migratsiyalarni tayyorladik. Endi ularga
haqiqiy HTTP orqali kirish — **CRUD** operatsiyalarini yozamiz.

## 1. Nega alohida Pydantic Schema kerak?

Django DRF'da `Serializer` bор edi — kirish/chiqish ma'lumotlarini
tekshirish va formatlash uchun. FastAPI'da bu vazifani **Pydantic
schema** bajaradi.

**MUHIM QOIDA:** SQLAlchemy modelini (`app/models/product.py`) to'g'ridan-to'g'ri
API response sifatida qaytarish **tavsiya etilmaydi**:
- Model — DB strukturasini ifodalaydi (internal)
- Schema — API orqali qanday ko'rinishini ifodalaydi (external)

Bu ikkisi har doim ham bir xil emas (masalan parolni hech qachon
qaytarmaslik kerak, yoki `category_id` o'rniga to'liq `category` obyektini
qaytarish kerak bo'lishi mumkin).

**Django solishtirma:**

| Django DRF | FastAPI |
|---|---|
| `serializers.ModelSerializer` | Pydantic `BaseModel` |
| `serializer.is_valid()` | avtomatik (`Depends`, request body) |
| `read_only_fields` | alohida Response schema |
| `serializer.save()` | `db.add()` + `db.commit()` |

## 2. Schema turlari — nega bir nechta kerak?

Bitta model uchun odatda **kamida 3 xil schema** yoziladi:

```python
# schemas/product.py
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    """Umumiy maydonlar — Create va Update uchun asos"""
    name: str
    price: float
    quantity: int = 0
    in_stock: bool = True
    category_id: int


class ProductCreate(ProductBase):
    """POST so'rovi uchun — hamma maydon majburiy (yoki default bilan)"""
    pass


class ProductUpdate(BaseModel):
    """PATCH so'rovi uchun — HAMMA maydon ixtiyoriy (qisman yangilash uchun)"""
    name: str | None = None
    price: float | None = None
    quantity: int | None = None
    in_stock: bool | None = None
    category_id: int | None = None


class ProductResponse(ProductBase):
    """GET javobida qaytariladigan shakl — id va DB'dan kelgan qo'shimcha maydonlar bilan"""
    id: int

    model_config = ConfigDict(from_attributes=True)
```

- **`ProductBase`** — umumiy maydonlar, boshqa schemalar shundan meros oladi
- **`ProductCreate`** — yaratish uchun (Django'dagi `serializer` write uchun)
- **`ProductUpdate`** — qisman yangilash uchun, hamma maydon `| None = None`
  (Django'dagi `partial=True` bilan bir xil g'oya)
- **`ProductResponse`** — javob uchun, `id` qo'shilgan
- **`model_config = ConfigDict(from_attributes=True)`** — Pydantic v2'da SQLAlchemy
  obyektidan to'g'ridan-to'g'ri o'qishga ruxsat beradi (eski nomi: `orm_mode = True`)

## 3. CRUD funksiyalarini alohida qatlamga chiqarish

Hammasini `main.py`ga yozish o'rniga, **CRUD logikasini** alohida faylga
ajratamiz — bu Django'dagi `services.py` yoki `managers.py` naqshiga
o'xshaydi, va Dars 23-24'da chuqurroq o'rganiladigan **Repository
Pattern**ning boshlang'ich shakli.

```python
# crud/product.py
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 10) -> list[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate) -> Product | None:
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    update_data = product.model_dump(exclude_unset=True)   # faqat berilgan maydonlar
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False

    db.delete(db_product)
    db.commit()
    return True
```

**`exclude_unset=True`** — bu `PATCH` uchun eng muhim qism: faqat
so'rovda **haqiqatan yuborilgan** maydonlarni oladi, qolganlarini
e'tiborsiz qoldiradi. Aks holda, `ProductUpdate`dagi `None` qiymatlar
mavjud ma'lumotlarni bo'sh qilib yuborishi mumkin edi.

## 4. Router — HTTP endpointlar

```python
# app/routers/product.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud import product as crud_product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return crud_product.create_product(db, product)


@router.get("/", response_model=list[ProductResponse])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_product.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud_product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud_product.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = crud_product.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
```

**Nega `status_code=204` DELETE uchun?** REST konvensiyasi bo'yicha,
muvaffaqiyatli `DELETE` — hech qanday body qaytarmaydi (`No Content`).
Django DRF'da `ModelViewSet`ning `destroy()` metodi ham xuddi shunday
ishlaydi.

## 5. `main.py`'da routerni ulash

```python
from fastapi import FastAPI
from app.routers import product, category

app = FastAPI(title="Storely CRUD", version="1.0.0")

app.include_router(category.router)
app.include_router(product.router)
```

Bu — Django'dagi `urls.py`'da `include()` bilan bir xil g'oya:
har bir resurs o'z faylida, `main.py` faqat ularni yig'adi.

## 6. HTTP status kodlari — qisqacha eslatma

| Amal | Status | Ma'nosi |
|---|---|---|
| `POST` (yaratish) | `201 Created` | Yangi resurs yaratildi |
| `GET` (o'qish) | `200 OK` | Muvaffaqiyatli qaytarildi |
| `PATCH` (qisman yangilash) | `200 OK` | Yangilandi, natija qaytariladi |
| `PUT` (to'liq almashtirish) | `200 OK` | Butunlay almashtirildi |
| `DELETE` (o'chirish) | `204 No Content` | O'chirildi, body yo'q |
| Topilmadi | `404 Not Found` | Resurs mavjud emas |

## 7. `PATCH` va `PUT` farqi

- **`PATCH`** — qisman yangilash (faqat yuborilgan maydonlar o'zgaradi)
- **`PUT`** — to'liq almashtirish (yuborilmagan maydonlar ham default'ga qaytishi kerak)

Amaliyotda ko'pchilik loyihalar faqat `PATCH`ni ishlatadi (soddaroq va
xavfsizroq), lekin ikkalasini ham bilish kerak.

## Xulosa

- **Schema (Pydantic)** ≠ **Model (SQLAlchemy)** — har biri o'z vazifasini
  bajaradi (Create/Update/Response uchun alohida)
- **CRUD funksiyalari** — alohida faylda (`crud/`), router'dan ajratilgan
  (Repository Pattern'ning boshlang'ich shakli)
- **`exclude_unset=True`** — `PATCH` uchun eng muhim texnika
- **Router** — har bir resurs o'z faylida, `main.py`'da `include_router()`
  orqali yig'iladi
- **Status kodlar** — REST konvensiyasiga rioya qilish muhim
  (`201`, `204`, `404` eng ko'p ishlatiladiganlari)