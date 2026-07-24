# Dars 19 — Password Hashing (Storely)

Bu dars — xavfsizlik asoslarining birinchi qadami: **parolni hech
qachon oddiy matnda saqlamaslik**. Agar DB o'g'irlansa yoki tasodifan
oshkor bo'lsa, xeshlangan parol foydalanuvchini himoya qiladi.

## 1. Nega oddiy saqlash xavfli?

```python
# HECH QACHON BUNDAY QILMANG!
user.password = "parol123"   # DB'da ochiq matn sifatida saqlanadi
```

Agar DB'ga kimdir kirsa (SQL injection, backup o'g'irlash, xodim
suiiste'moli), **barcha foydalanuvchilarning haqiqiy parollari** ochiladi.
Odamlar ko'pincha bir xil parolni boshqa saytlarda ham ishlatishadi —
bu butun zanjir bo'ylab xavf tug'diradi.

**Django solishtirma:** Django `User.objects.create_user()` ichida
avtomatik `PBKDF2` bilan xeshlaydi. FastAPI'da buni **qo'lda** sozlaymiz
— bu, aslida, tizim qanday ishlashini chuqurroq tushunish imkonini beradi.

## 2. Xeshlash nima, shifrlashdan farqi?

- **Shifrlash (encryption)** — qaytarib bo'ladi (`decrypt` bilan asl
  qiymatni olish mumkin), kalit kerak
- **Xeshlash (hashing)** — **bir tomonlama**, qaytarib bo'lmaydi.
  Faqat "bu parol shu xeshga mos keladimi?" deb solishtirish mumkin

Parollar uchun **har doim xeshlash** ishlatiladi, shifrlash emas —
chunki hatto administratorning o'zi ham foydalanuvchi parolini
"o'qiy olmasligi" kerak.

## 3. Nega oddiy `hashlib.sha256()` yetarli emas?

```python
# YOMON — buni qilmang!
import hashlib
hashed = hashlib.sha256("parol123".encode()).hexdigest()
```

Muammolar:
- **Juda tez ishlaydi** — zamonaviy GPU sekundiga milliardlab
  variantni sinab ko'rishi mumkin (`brute-force` hujum)
- **`salt` yo'q** — agar ikki foydalanuvchi bir xil parolni ishlatsa,
  ularning xeshi ham bir xil bo'ladi (`rainbow table` hujumiga ochiq)

**Parollar uchun maxsus, ataylab SEKIN ishlaydigan algoritmlar
ishlatiladi**: `bcrypt`, `argon2`, `scrypt`. Sekinlik — bu yerda
**xususiyat**, kamchilik emas (chunki brute-force hujumni sekinlashtiradi).

## 4. O'rnatish

```powershell
pip install "passlib[bcrypt]"
```

`requirements.txt`ga qo'shing:

```
passlib[bcrypt]
```
## 5. `core/security.py` — xeshlash funksiyalari

```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Parolni xeshlash — ro'yxatdan o'tishda ishlatiladi"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiritilgan parolni saqlangan xesh bilan solishtirish — login'da ishlatiladi"""
    return pwd_context.verify(plain_password, hashed_password)
```

**`CryptContext`** — passlib'ning asosiy klassi, bir nechta algoritmni
qo'llab-quvvatlaydi va ularni avtomatik "eskirgan" deb belgilaydi
(`deprecated="auto"` — agar kelajakda algoritm o'zgartirilsa, eski
xeshlar ham hali tekshirilishi mumkin, lekin yangi parollar yangi
algoritm bilan xeshlanadi).

## 6. `User` modeli

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
```

**MUHIM:** ustun nomi **`hashed_password`**, `password` emas — bu,
kod o'qigan har bir kishiga (jumladan sizga, olti oydan keyin) "bu
maydon xeshlangan holda saqlanadi" degan signalni beradi. Hech qachon
`password` deb nomlamang — bu chalkashtiradi va xato qilish xavfini
oshiradi.

## 7. Schema — parolni faqat KIRISH uchun qabul qilish, chiqishda hech qachon qaytarmaslik

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str   # <- faqat KIRISH uchun, oddiy matn holida qabul qilinadi


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    # E'TIBOR: bu yerda "password" YOKI "hashed_password" YO'Q!
```

**Bu — eng muhim xavfsizlik qoidasi:** `UserResponse`da **hech qachon**
parol yoki xesh maydoni bo'lmasligi kerak. Agar tasodifan `hashed_password`ni
ham qo'shib qo'ysangiz, API javobida foydalanuvchining xeshi (garchi u
"faqat xesh" bo'lsa ham) tashqariga chiqib ketadi — bu keraksiz xavf.

`EmailStr` ishlatish uchun qo'shimcha kutubxona kerak:
```powershell
pip install pydantic[email]
```

## 8. CRUD — ro'yxatdan o'tish

```python
# app/crud/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed = hash_password(user.password)   # <- parol shu yerda xeshlanadi
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

**E'tibor bering:** `UserCreate`dan kelgan `user.password` (oddiy matn)
**hech qachon** to'g'ridan-to'g'ri `User` modeliga yozilmaydi — u avval
`hash_password()` orqali o'tkaziladi, va natija `hashed_password`
ustuniga saqlanadi.

## 9. Router — ro'yxatdan o'tish endpointi

```python
# app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud import user as crud_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu email allaqachon ro'yxatdan o'tgan")

    return await crud_user.create_user(db, user)
```

## 10. Sinash
```bash
POST /users/register
Content-Type: application/json

{
  "email": "aziz@example.com",
  "password": "MenSirliParolim123",
  "full_name": "Aziz Karimov"
}
```

Javobda **`password` yoki `hashed_password` bo'lmasligi** kerak:
```json
{
  "id": 1,
  "email": "aziz@example.com",
  "full_name": "Aziz Karimov",
  "is_active": true
}
```

DB'ni tekshirsangiz (`PRAGMA table_info` yoki debug endpoint orqali),
`hashed_password` ustunida `$2b$12$...` kabi uzun, tasodifiy ko'rinishdagi
qator borligini ko'rasiz — bu, **hech qachon** asl parolga qaytarib
bo'lmaydigan xesh.

## Xulosa

- **Xeshlash ≠ shifrlash** — bir tomonlama, qaytarib bo'lmaydi
- **`bcrypt`** — ataylab sekin, brute-force hujumga chidamli
- **`hashed_password`** — ustun nomi aniq bo'lishi kerak, `password` emas
- **`UserResponse`da parol maydoni YO'Q** — bu eng muhim xavfsizlik qoidasi
- **`verify_password()`** — Dars 20'da login qilishda ishlatiladi
  (kiritilgan parolni saqlangan xesh bilan solishtirish uchun)

## Amaliy struktura

```
dars-19-password-hashing/
├── README.md
├── requirements.txt
├── alembic.ini
├── alembic/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_users.py
└── app/
    ├── __init__.py
    ├── main.py
    ├── database.py
    ├── core/                  <- YANGI papka
    │   ├── __init__.py
    │   └── security.py
    ├── models/
    │   ├── __init__.py
    │   ├── category.py
    │   ├── product.py
    │   └── user.py             <- YANGI
    ├── schemas/
    │   ├── __init__.py
    │   ├── category.py
    │   ├── product.py
    │   └── user.py              <- YANGI
    ├── crud/
    │   ├── __init__.py
    │   ├── category.py
    │   ├── product.py
    │   └── user.py               <- YANGI
    └── routers/
        ├── __init__.py
        ├── category.py
        ├── product.py
        └── user.py                <- YANGI

```

