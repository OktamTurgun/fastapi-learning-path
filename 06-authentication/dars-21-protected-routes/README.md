# Dars 21 — Protected Routes (Storely)

Dars 20'da JWT token yaratishni o'rgandik. Endi bu tokenni **haqiqiy
ishga soladigan** qismga o'tamiz: `Depends()` orqali "joriy foydalanuvchi"
dependency yozib, ba'zi endpointlarni himoyalaymiz.

## 1. Qanday ishlaydi? (umumiy oqim)

1. Foydalanuvchi `POST /users/login` orqali token oladi
2. Har bir keyingi so'rovda, u tokenni **`Authorization: Bearer <token>`**
   headerida yuboradi
3. Server maxsus **dependency** orqali headerdan tokenni o'qiydi,
   uni tekshiradi (`decode_access_token`), va agar to'g'ri bo'lsa —
   tegishli `User` obyektini DB'dan topib, endpoint funksiyasiga uzatadi
4. Agar token yo'q, noto'g'ri, yoki muddati tugagan bo'lsa — `401`
   xatosi qaytariladi, endpoint **ishga tushmaydi**

**Django solishtirma:** Bu — DRF'dagi `IsAuthenticated` permission
class + `request.user`ning FastAPI'dagi qo'lda yozilgan ekvivalenti.

## 2. `OAuth2PasswordBearer` — tokenni headerdan olish

FastAPI'da tokenni headerdan olish uchun maxsus, tayyor sinf bor:

```python
# app/core/security.py ichiga qo'shiladi
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
```

**Bu nima qiladi?** `OAuth2PasswordBearer` — Swagger UI'da avtomatik
**"Authorize" tugmasi** paydo bo'lishini ta'minlaydi, va so'rovdan
`Authorization: Bearer <token>` headerini o'qib, faqat `<token>`
qismini ajratib beradi. `tokenUrl="users/login"` — bu shunchaki
Swagger UI'ga "token qayerdan olinadi" deb ko'rsatish uchun, boshqa
funksional ta'siri yo'q.

## 3. `get_current_user` — eng muhim dependency

```python
# app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.crud import user as crud_user
from app.models.user import User


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kirish huquqi tasdiqlanmadi",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await crud_user.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    return user
```

**Diqqat:** `crud_user.get_user_by_id` — bu yangi funksiya, uni
`crud/user.py`ga qo'shishingiz kerak bo'ladi (Dars 20'da faqat
`get_user_by_email` bor edi).

**Nima uchun bu — "dependency ichida dependency"?** `get_current_user`
o'zi ikkita boshqa dependency'ga bog'liq: `oauth2_scheme` (tokenni
headerdan olish) va `get_db` (DB session). FastAPI bularni avtomatik
"zanjir" qilib, to'g'ri tartibda chaqiradi — bu, Django DRF'dagi
bir nechta permission class'larni birlashtirishga o'xshaydi.

## 4. `is_active` tekshiruvi — qo'shimcha xavfsizlik qatlami

```python
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Foydalanuvchi faol emas")
    return current_user
```

Bu — ikkinchi dependency, agar foydalanuvchi (masalan administrator
tomonidan) bloklangan bo'lsa (`is_active=False`), token hali amal
qilsa ham, kirishga ruxsat bermaydi.

## 5. Himoyalangan endpoint — `GET /users/me`

```python
# app/routers/user.py ichiga qo'shiladi
from app.core.dependencies import get_current_active_user

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user
```

Bu — **eng sodda himoyalangan endpoint**: token to'g'ri bo'lsa,
foydalanuvchi o'zi haqidagi ma'lumotni oladi.

## 6. Mahsulot qo'shishni himoyalash (real stsenariy)

Endi `POST /products/`ni **faqat login qilgan foydalanuvchilar**
uchun cheklaymiz:

```python
# app/routers/product.py — create_product funksiyasi yangilanadi
from app.core.dependencies import get_current_active_user
from app.models.user import User

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),   # <- himoya qo'shildi
):
    return await crud_product.create_product(db, product)
```

**E'tibor bering:** `current_user` parametri funksiya ichida
ishlatilmasa ham, `Depends(get_current_active_user)` yozilishining
o'zi — himoya vazifasini bajaradi. Agar token noto'g'ri bo'lsa,
funksiya tanasi **hech qachon ishga tushmaydi**, `401` qaytadi.

Xohlasangiz, kim yaratganini ham saqlashingiz mumkin (bu — kelajakda
"faqat o'z mahsulotingizni o'chirish" kabi funksiyalar uchun kerak
bo'ladi), lekin bu — bu darsning doirasidan tashqarida (bu — Dars 25:
Permissions & Roles'da chuqurroq ko'riladi).

## 7. Swagger UI'da sinash

`/docs`ga kirganingizda, endi yuqori o'ng burchakda **"Authorize"**
tugmasi paydo bo'ladi. Bosganingizda, `username`/`password` so'raladi
— lekin bizning tizimimizda **JSON body orqali login** ishlatilgani
uchun, bu forma **to'g'ridan-to'g'ri ishlamaydi**. Buning o'rniga,
qo'lda test qilish uchun:

1. `POST /users/login` orqali token oling
2. Tokenni nusxalang
3. Har bir himoyalangan endpoint yonidagi **qulf belgisi**ni bosib,
   yoki to'g'ridan-to'g'ri headerga qo'shib sinang:

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

**Eslatma:** Agar to'liq OAuth2 formasi (`username`/`password` orqali
avtomatik login) kerak bo'lsa, alohida `/token` endpointi
`OAuth2PasswordRequestForm` bilan yozilishi kerak — bu, ko'pincha
Swagger UI qulayligi uchun qo'shiladi, lekin bizning JSON-based
`login`imiz bilan **parallel** ishlaydi. Buni ixtiyoriy bonus sifatida
pastda ko'rsatamiz.

## 8. Sinash misoli (`curl` yoki Swagger orqali)

```bash
## 8. Sinash misoli (`curl` yoki Swagger orqali)

POST /users/login
{"email": "aziz@example.com", "password": "MenSirliParolim123"}
→ {"access_token": "eyJ...", "token_type": "bearer"}

GET /users/me
Header: Authorization: Bearer eyJ...
→ {"id": 1, "email": "aziz@example.com", "full_name": "...", "is_active": true}

GET /users/me
Header: (tokensiz)
→ 401 {"detail": "Not authenticated"}

POST /products/
Header: Authorization: Bearer eyJ... (noto'g'ri yoki eskirgan token)
→ 401 {"detail": "Kirish huquqi tasdiqlanmadi"}
```
## Xulosa

- **`OAuth2PasswordBearer`** — tokenni `Authorization` headeridan
  o'qish uchun standart FastAPI vositasi
- **`get_current_user`** — token orqali `User` obyektini olish uchun
  markaziy dependency, `Depends()` zanjiri orqali ishlaydi
- **`get_current_active_user`** — qo'shimcha `is_active` tekshiruvi
  bilan
- **Himoyalash — bir qatorli o'zgarish**: `Depends(get_current_active_user)`
  qo'shish kifoya, funksiya tanasini o'zgartirish shart emas
- **`GET /users/me`** — "men kimman" endpointi, eng oddiy himoyalangan
  misol

## Amaliy struktura

```
dars-21-protected-routes/
├── README.md
├── requirements.txt
├── alembic.ini
├── alembic/
├── tests/
│   └── (eski testlar + test_protected_routes.py YANGI)
└── app/
    ├── core/
    │   ├── security.py         <- YANGILANADI (oauth2_scheme qo'shiladi)
    │   └── dependencies.py       <- YANGI (get_current_user, get_current_active_user)
    ├── crud/
    │   └── user.py                <- YANGILANADI (get_user_by_id qo'shiladi)
    └── routers/
        ├── user.py                  <- YANGILANADI (GET /users/me qo'shiladi)
        └── product.py                <- YANGILANADI (POST himoyalanadi)
```
