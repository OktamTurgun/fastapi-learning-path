# Dars 13 — ORM Models, Relationship, ForeignKey (Storely asosida)

Bu darsda birinchi marta **haqiqiy jadval** yaratasiz — bu safar
Storely loyihangiz uchun `Category` va `Product` modellarini quramiz.
Shu yerdan boshlab, statik `list`/`dict` o'rniga ma'lumotlar **SQLite
faylida** saqlanadi.

## 1. ORM Model nima?

Dars 12'da yaratilgan `Base` klassidan meros olib, har bir jadval uchun
alohida Python klassi yoziladi:

```python
from sqlalchemy import Column, Integer, String
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
```

- `__tablename__` — bu klass qaysi jadvalga mos kelishini bildiradi
- `Column(...)` — jadvaldagi bitta ustun
- `primary_key=True` — bu ustun jadvalning asosiy kaliti (odatda `id`)
- `nullable=False` — bu ustun **majburiy**
- `unique=True` — bu ustunda takrorlanadigan qiymat bo'lishi mumkin emas
  (masalan ikkita bir xil nomli kategoriya bo'lmasin)

**Django DRF bilan solishtirish:** Bu — aynan Django'dagi
`models.Model`dan meros olib, `CharField`, `IntegerField` yozishga
o'xshaydi.

## 2. Asosiy ustun turlari

| SQLAlchemy turi | Ma'nosi | Django ekvivalenti |
|---|---|---|
| `Integer` | Butun son | `IntegerField` |
| `String` | Matn | `CharField` |
| `Text` | Uzun matn | `TextField` |
| `Float` | Kasr son | `FloatField` |
| `Boolean` | True/False | `BooleanField` |
| `DateTime` | Sana va vaqt | `DateTimeField` |

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 3. ForeignKey — jadvallarni bog'lash

Storely'da har bir mahsulot **bitta** kategoriyaga tegishli (masalan
"Elektronika", "Kiyim-kechak"). Bu — **ForeignKey** orqali ifodalanadi:

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))   # <- bog'lanish!
```

`ForeignKey("categories.id")` — "bu ustun `categories` jadvalining `id`
ustuniga ishora qiladi" degani. Django'dagi
`ForeignKey(Category, on_delete=models.CASCADE)` bilan bir xil g'oya.

## 4. `relationship()` — ikki tomonlama bog'lanish

`ForeignKey` faqat DB darajasida bog'laydi. Python darajasida qulay
ishlash uchun (masalan `product.category.name` deb yozish uchun),
**`relationship()`** kerak:

```python
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="products")
```

Endi Python kodida:
```python
product.category.name        # mahsulotning kategoriyasi nomi
category.products              # kategoriyadagi barcha mahsulotlar (list)
```

`back_populates` — ikkala tomonni bir-biriga "bog'lab qo'yadi", shunda
SQLAlchemy ikkalasi ham **bir xil munosabatning ikki tomoni** ekanini
biladi.

## 5. Munosabat turlari (Storely kontekstida)

| Turi | Storely misoli |
|---|---|
| **One-to-Many** | Bir kategoriya — ko'p mahsulot (hozirgi dars) |
| **Many-to-One** | Ko'p mahsulot — bir kategoriya (xuddi shu, teskari) |
| **One-to-One** | Bir mahsulot — bitta batafsil tavsif profili |
| **Many-to-Many** | Ko'p mahsulot — ko'p teg (masalan "chegirma", "yangi") |

Keyingi modullarda (Dars 15-17, Delivery API) siz yana ko'radigan
munosabat: `Order → OrderItem → Product` — bu ham One-to-Many
zanjirining davomi.

### Kelajakdagi Many-to-Many misoli (hozircha faqat ko'rish uchun)

```python
from sqlalchemy import Table

product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    tags = relationship("Tag", secondary=product_tags, back_populates="products")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    products = relationship("Product", secondary=product_tags, back_populates="tags")
```

Bu — masalan "chegirmadagi mahsulotlar" yoki "yangi kelganlar" kabi
teglash tizimi kerak bo'lganda ishlatiladi. Hozircha shart emas.

## 6. Jadvallarni haqiqatan yaratish — `Base.metadata.create_all()`

Modellarni yozish hali jadval **yaratmaydi** — buni ishga tushirish kerak:

```python
from app.database import Base, engine
from app.models import Category, Product   # modellar import qilinishi SHART

Base.metadata.create_all(bind=engine)
```

**MUHIM ESLATMA:** Bu usul — faqat **o'rganish va boshlang'ich bosqich**
uchun. Real loyihada (Dars 14'dan boshlab, Alembic bilan) jadval yaratish
va o'zgartirish migratsiya fayllari orqali boshqariladi — chunki
`create_all()` mavjud jadvalni **o'zgartira olmaydi** (masalan Storely'ga
keyinchalik `discount_percent` degan yangi ustun qo'shmoqchi bo'lsangiz,
`create_all()` buni qila olmaydi, Alembic esa qila oladi).

## 7. Modellarni fayllarga qanday bo'lish kerak (tavsiya)

app/
├── models/
│   ├── init.py
│   ├── category.py
│   └── product.py

Bu — Dars 04'dagi routerlarni fayllarga bo'lish naqshining xuddi shu
tamoyili, endi modellar uchun. Storely kattalashganda (`Order`, `User`,
`Customer` qo'shilganda), har biri o'z faylida bo'ladi.

## Xulosa

- **Model klass** — `Base`dan meros oladi, `__tablename__` va `Column`lar
  bilan jadval strukturasini belgilaydi
- **`ForeignKey`** — DB darajasida jadvallarni bog'laydi
  (`Product.category_id → Category.id`)
- **`relationship()`** — Python darajasida qulay ikki tomonlama
  bog'lanish (`back_populates` bilan)
- **`Category → Product`** — Storely'dagi birinchi va eng asosiy
  One-to-Many munosabat, keyingi darslarda `Order`, `Customer` shu
  negiz ustiga quriladi