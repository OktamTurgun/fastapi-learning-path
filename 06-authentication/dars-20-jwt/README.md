# Dars 20 — JWT (Storely)

Dars 19'da parolni xavfsiz saqlashni o'rgandik. Endi savol: foydalanuvchi
login qilgandan keyin, u **har bir keyingi so'rovda** "menman" deb qanday
isbotlaydi? HTTP — **stateless** (holatsiz) protokol, server so'rovlar
orasida hech narsani "eslab qolmaydi". Buning yechimi — **JWT**.

## 1. JWT nima?

**JWT (JSON Web Token)** — foydalanuvchi haqida ma'lumotni (masalan
`user_id`, `email`) o'z ichiga olgan, **raqamli imzolangan** matn qatori.
Server buni yaratadi, foydalanuvchiga beradi, foydalanuvchi esa har bir
so'rovda uni qaytarib yuboradi (odatda `Authorization` headerida).

**Django solishtirma:** Django'da odatda **session-based auth**
ishlatiladi (cookie + server xotirasida session ma'lumoti). JWT esa
**stateless** — server hech narsani saqlamaydi, token o'zi barcha
kerakli ma'lumotni tashiydi. Bu, ayniqsa mikroservis arxitekturasida
yoki mobil ilovalar bilan ishlaganda foydali (DRF'da bu — `djangorestframework-simplejwt`
kutubxonasi bilan bir xil g'oya).

## 2. JWT tuzilishi — 3 qism

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzM3MDAwMDAwfQ.4f8a...
└──────────── HEADER ────────────┘.└──────── PAYLOAD ────────┘.└─ SIGNATURE ─┘

- **Header** — qaysi algoritm ishlatilgani (`HS256`)
- **Payload** — haqiqiy ma'lumot (`user_id`, `exp` — muddati tugash vaqti)
- **Signature** — server **maxfiy kaliti** (`SECRET_KEY`) bilan
  Header+Payload'ni imzolagan natija

**MUHIM:** Payload — **shifrlanmagan**, faqat Base64 bilan kodlangan!
Har kim uni ochib o'qiy oladi (masalan jwt.io saytida). Lekin
**o'zgartira olmaydi** — chunki `SECRET_KEY` bilmasdan yangi to'g'ri
`Signature` yasab bo'lmaydi. Shuning uchun **hech qachon** payload'ga
parol yoki boshqa maxfiy ma'lumot qo'ymang.

## 3. O'rnatish

```powershell
pip install "python-jose[cryptography]"
```

`requirements.txt`ga qo'shing:

```txt
python-jose[cryptography]
```
## 4. `SECRET_KEY` — muhim xavfsizlik elementi

```python
# app/core/config.py
import secrets

# Productionda bu .env faylidan o'qiladi, hech qachon kodga yozilmaydi!
SECRET_KEY = "your-secret-key-CHANGE-THIS-IN-PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

**Ishlab chiqarishda qanday kalit generatsiya qilinadi:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Bu — tasodifiy, uzun (64 belgili) qator yaratadi. Buni **hech qachon
Git'ga commit qilmang** — `.env` faylida saqlanadi (`.gitignore`da).
Hozircha, o'rganish maqsadida, oddiy qator bilan davom etamiz, lekin
Dars 27-28'da (Docker, Deployment) buni to'g'ri `.env`ga ko'chiramiz.

## 5. Token yaratish va tekshirish funksiyalari

```python
# app/core/security.py — qo'shimcha qilinadi (Dars 19'dagi hash_password/verify_password bilan birga)
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key-CHANGE-THIS-IN-PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    """JWT token yaratish — login muvaffaqiyatli bo'lganda chaqiriladi"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Token'ni tekshirish va ichidagi ma'lumotni olish"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**`exp` (expiration) nima uchun muhim?** Agar token **hech qachon
tugamasa**, va u o'g'irlansa (masalan XSS orqali), tajovuzkor **abadiy**
o'sha foydalanuvchi nomidan harakat qila oladi. `exp` bilan token
ma'lum vaqtdan keyin (bizda 30 daqiqa) avtomatik yaroqsiz bo'ladi.

## 6. Login endpoint — `POST /users/login`

```python
# app/schemas/token.py
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str
```

```python
# app/routers/user.py ichiga qo'shiladi
from app.schemas.token import Token, LoginRequest
from app.core.security import verify_password, create_access_token


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")
```

**MUHIM XAVFSIZLIK QOIDASI:** Xato xabari **har doim bir xil** bo'lishi
kerak — "Email yoki parol noto'g'ri", **"Email topilmadi"** yoki
**"Parol noto'g'ri"** deb **alohida-alohida aytilmaydi**. Aks holda,
tajovuzkor qaysi emaillar ro'yxatdan o'tganini "sinab ko'rish" orqali
bilib olishi mumkin (bu — **user enumeration** hujumi deb ataladi).

**`"sub"` nima?** JWT standartida `sub` (subject) — token kimga
tegishli ekanini bildiruvchi standart maydon. Odatda foydalanuvchi
`id`si shu yerga yoziladi (matn ko'rinishida, chunki JWT standarti
`sub`ni string sifatida talab qiladi).

## 7. Sinash

```powershell
POST /users/login
{"email": "aziz@example.com", "password": "MenSirliParolim123"}
```
Javob:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Bu tokenni [jwt.io](https://jwt.io) saytiga joylashtirsangiz (**faqat
o'rganish uchun, hech qachon haqiqiy production token bilan qilmang!**),
payload ichida `{"sub": "1", "exp": 1737000000}` kabi ma'lumotni
ko'rasiz — bu, tokenning **kim ekanini** va **qachon tugashini** o'zida
tashiganini isbotlaydi.

## 8. Noto'g'ri parol bilan sinash

```powershell
POST /users/login
{"email": "aziz@example.com", "password": "notogriParol"}
```

Javob: `401 {"detail": "Email yoki parol noto'g'ri"}`

## Xulosa

- **JWT — stateless**, server hech narsani saqlamaydi, token o'zi
  ma'lumotni tashiydi
- **Payload — shifrlanmagan** (faqat Base64), shuning uchun **maxfiy
  ma'lumot** (parol) hech qachon tokenga qo'yilmaydi
- **`SECRET_KEY`** — token imzosini yaratish/tekshirish uchun, hech
  qachon oshkor qilinmaydi yoki Git'ga commit qilinmaydi
- **`exp`** — token muddati, xavfsizlik uchun majburiy
- **Bir xil xato xabari** — login xato sabablarini alohida ko'rsatmaslik
  (user enumeration hujumidan himoya)
- Bu dars **faqat token yaratadi** — Dars 21'da bu tokenni **himoyalangan
  endpointlarni himoya qilish** uchun ishlatamiz

## Amaliy struktura

```
dars-20-jwt/
├── README.md
├── requirements.txt
├── alembic.ini
├── alembic/
├── tests/
│   └── (Dars 19'dagilar + test_login.py YANGI)
└── app/
    ├── core/
    │   ├── __init__.py
    │   ├── security.py       <- YANGILANADI (create_access_token, decode_access_token qo'shiladi)
    │   └── config.py          <- YANGI
    ├── schemas/
    │   ├── ...
    │   └── token.py            <- YANGI
    └── routers/
        └── user.py              <- YANGILANADI (login endpoint qo'shiladi)
```

```powershell
xcopy ..\dars-19-password-hashing\app app\ /E /I
xcopy ..\dars-19-password-hashing\alembic alembic\ /E /I
copy ..\dars-19-password-hashing\alembic.ini alembic.ini
xcopy ..\dars-19-password-hashing\tests tests\ /E /I
copy ..\dars-19-password-hashing\pytest.ini pytest.ini

pip install "python-jose[cryptography]"
```