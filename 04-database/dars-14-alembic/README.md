# Dars 14 — Alembic (Migration)

Dars 13'da `Base.metadata.create_all()` bilan jadval yaratdik. Bu usul
oddiy, lekin **jiddiy cheklovga** ega: mavjud jadvalni o'zgartira olmaydi.
Alembic — aynan shu muammoni hal qiladi: Django'dagi
`makemigrations` + `migrate` juftligining SQLAlchemy ekvivalenti.

## 1. Nega Alembic kerak?

Storely rivojlanayapti deylik — `Product` modeliga yangi ustun
qo'shmoqchisiz: `discount_percent`. Agar modelga qo'shib, keyin
serverni qayta ishga tushirsangiz:

- `create_all()` — hech narsa qilmaydi, chunki jadval **allaqachon mavjud**
  (u faqat yo'q jadvallarni yaratadi, mavjudlarini tekshirmaydi ham)
- Natija: kodda `discount_percent` bor, DB'da yo'q → ishga tushganda xatolik

**Django solishtirma:**

| Django | Alembic |
|---|---|
| `python manage.py makemigrations` | `alembic revision --autogenerate` |
| `python manage.py migrate` | `alembic upgrade head` |
| `migrations/0001_initial.py` | `alembic/versions/xxxx_initial.py` |
| `python manage.py showmigrations` | `alembic history` |

Farqi: Django migratsiyalarni **avtomatik** boshqaradi (bitta buyruq
ketma-ketligi), Alembic esa har bir bosqichni siz nazorat qilishingizni
talab qiladi — bu ko'proq ish, lekin ko'proq erkinlik va shaffoflik
beradi.

## 2. O'rnatish

```powershell
pip install alembic
```

`requirements.txt`'ga qo'shing:

```text
alembic==1.13.2
```
## 3. Ishga tushirish — `alembic init`

```powershell
alembic init alembic
```
```text
Bu quyidagi strukturani yaratadi:

dars-14-alembic/
├── alembic/
│   ├── versions/          <- har bir migratsiya shu yerda saqlanadi
│   ├── env.py              <- Alembic konfiguratsiyasi (MUHIM fayl)
│   └── script.py.mako      <- yangi migratsiya shabloni
├── alembic.ini              <- asosiy config fayl
└── app/
├── database.py
└── models/
```

## 4. `alembic.ini` — DB manzilini sozlash

`alembic.ini` faylida quyidagi qatorni toping va o'zgartiring:

```ini
sqlalchemy.url = sqlite:///./storely.db
```

**Eslatma:** Productionda bu qatorni to'g'ridan-to'g'ri yozish tavsiya
etilmaydi (parol ochiq ko'rinadi). Buning o'rniga `env.py` ichida
`.env`'dan o'qib olamiz (pastda ko'rsatiladi).

## 5. `env.py` — modellarni Alembic'ga tanishtirish

Bu — eng ko'p unutiladigan qadam. Agar buni qilmasangiz, `autogenerate`
sizning modellaringizni **ko'rmaydi** va bo'sh migratsiya yaratadi.

`alembic/env.py` faylida ikkita joyni o'zgartirish kerak:

```python
# env.py fayl boshida, mavjud importlardan keyin qo'shing:
import sys
import os
sys.path.append(os.getcwd())   # loyiha root'ini Python yo'liga qo'shish

from app.database import Base
from app.models import Category, Product   # BARCHA modellar import qilinishi SHART

# target_metadata = None qatorini toping va shunga almashtiring:
target_metadata = Base.metadata
```

**Nega modellarni import qilish shart?** `Base.metadata` faqat
**import qilingan** modellarni "biladi". Agar `Product` modelini import
qilmasangiz, u fayl mavjud bo'lsa ham, Alembic uni jadval sifatida
ko'rmaydi va autogenerate uni tashlab ketadi.

## 6. Birinchi migratsiya — `autogenerate`

```powershell
alembic revision --autogenerate -m "create categories and products tables"
```

Bu `alembic/versions/` ichida yangi fayl yaratadi, masalan:
`a1b2c3d4e5f6_create_categories_and_products_tables.py`

Ichida ikkita asosiy funksiya bo'ladi:

```python
def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # ... products jadvali ham shu yerda

def downgrade() -> None:
    op.drop_table('products')
    op.drop_table('categories')
```

- **`upgrade()`** — migratsiyani qo'llash (jadval yaratish/o'zgartirish)
- **`downgrade()`** — migratsiyani bekor qilish (orqaga qaytarish)

**MUHIM:** Autogenerate har doim ham 100% to'g'ri kod yozavermaydi
(masalan `unique=True` ba'zan sezilmasligi mumkin). Har doim generatsiya
qilingan faylni **qo'lda ko'zdan kechiring**, keyingina `upgrade` qiling.

## 7. Migratsiyani qo'llash — `alembic upgrade`

```powershell
alembic upgrade head
```

`head` — "eng oxirgi migratsiyagacha" degani. Natijada `storely.db`
faylida `categories` va `products` jadvallari yaratiladi, va yana bitta
maxsus jadval: `alembic_version` — bu jadval hozir qaysi migratsiya
qo'llanganini kuzatib boradi (Django'dagi `django_migrations` jadvaliga
o'xshash).

## 8. Jadvalga yangi ustun qo'shish (real stsenariy)

Storely'ga `discount_percent` qo'shamiz. Avval modelni o'zgartiring:

```python
# app/models/product.py
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    discount_percent = Column(Integer, default=0)   # <- YANGI ustun
```

Keyin yangi migratsiya yarating:

```powershell
alembic revision --autogenerate -m "add discount_percent to products"
alembic upgrade head
```

Alembic avtomatik quyidagini generatsiya qiladi:

```python
def upgrade() -> None:
    op.add_column('products', sa.Column('discount_percent', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('products', 'discount_percent')
```

Ana shu — `create_all()` **hech qachon** qila olmaydigan narsa.

## 9. Orqaga qaytarish — `alembic downgrade`

```powershell
alembic downgrade -1        # bitta migratsiyani orqaga qaytarish
alembic downgrade base      # hamma migratsiyalarni bekor qilish
alembic upgrade head        # yana oldinga
```

## 10. Foydali buyruqlar

| Buyruq | Vazifasi |
|---|---|
| `alembic current` | hozirgi migratsiya holatini ko'rsatadi |
| `alembic history` | barcha migratsiyalar tarixi |
| `alembic history --verbose` | tarix + tavsif bilan |
| `alembic show <revision>` | bitta migratsiya haqida batafsil |
| `alembic heads` | oxirgi migratsiya(lar) ID'si |

## 11. `.env` bilan xavfsiz sozlash (tavsiya etiladi)

`env.py`'da `alembic.ini`'dagi qattiq yozilgan URL o'rniga:

```python
# env.py ichida, config yuklangandan keyin
import os
from dotenv import load_dotenv

load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
```

`.env`:

```text
DATABASE_URL=sqlite:///./storely.db
```

Bu — parol/manzilni Git'ga tushib qolishidan saqlaydi (`.env`
`.gitignore`'da bo'lishi shart).

## Xulosa

- **`create_all()`** — faqat boshlang'ich, mavjud jadvalni o'zgartira
  olmaydi
- **Alembic** — jadval strukturasidagi har bir o'zgarishni versiyalab,
  qaytarib bo'ladigan qilib boshqaradi (Django `migrations/`ga o'xshash)
- **`env.py`**'da modellarni import qilish va `target_metadata = Base.metadata`
  — eng ko'p unutiladigan, lekin eng muhim qadam
- **Workflow:** modelni o'zgartir → `alembic revision --autogenerate`
  → faylni tekshir → `alembic upgrade head`
- **`upgrade()` / `downgrade()`** — har bir migratsiya ikki yo'nalishga
  ham ega bo'lishi kerak

## Amaliy structura

```text 
dars-14-alembic/
├── README.md
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── app/
    ├── __init__.py
    ├── main.py
    ├── database.py
    └── models/
        ├── __init__.py
        ├── category.py
        └── product.py

```
Bu — Dars 13'dagi Storely app/ papkasining aynan o'zi (database.py, models/). Faqat ustiga alembic/ qo'shiladi.