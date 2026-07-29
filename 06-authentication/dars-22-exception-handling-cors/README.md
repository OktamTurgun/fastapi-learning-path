# Dars 22 — Exception Handling & CORS (Storely)

Bu dars — API'ni **frontend bilan ishlashga tayyor** qiladigan so'nggi
qatlam: izchil xato formatlari va CORS sozlamalari.

## 1. Nega global exception handler kerak?

Hozirgi holatda, har bir joyda `HTTPException(status_code=404, detail="...")`
yozasiz. Bu ishlaydi, lekin:
- Xato formati **hamma joyda bir xil bo'lishi kafolatlanmagan** (masalan
  ba'zi joyda `{"detail": "..."}`, boshqa joyda boshqacha struktura
  bo'lib qolishi mumkin)
- Kutilmagan xatolar (masalan kod xatosi, `ZeroDivisionError`) — default
  holda foydalanuvchiga **butun Python traceback**ni ko'rsatishi mumkin
  (bu — xavfsizlik muammosi, chunki bu ichki kod strukturasini oshkor qiladi)

**Django solishtirma:** Bu — Django DRF'dagi `exception_handler`
sozlamasining FastAPI ekvivalenti (`settings.py`dagi
`EXCEPTION_HANDLER`).

## 2. Global exception handler — `app/core/exceptions.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic validatsiya xatolarini izchil formatga keltirish"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validatsiya xatosi", "errors": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Kutilmagan (dasturchi bashorat qilmagan) xatolarni ushlab qolish"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Serverda kutilmagan xatolik yuz berdi"},
    )
```

**MUHIM:** `generic_exception_handler` — foydalanuvchiga **hech qachon**
haqiqiy xato matnini (masalan `AttributeError: 'NoneType' object has no
attribute 'x'`) ko'rsatmaydi. Bu xavfsizlik uchun juda muhim — aks holda
tajovuzkor kodning ichki strukturasi haqida ma'lumot olishi mumkin.
Productionda, haqiqiy xato matni faqat **server loglariga** yoziladi
(`logging` orqali — bu, kelajakda alohida darsda chuqurroq o'rganiladi).

## 3. `main.py`da handlerlarni ro'yxatdan o'tkazish

```python
# app/main.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import validation_exception_handler, generic_exception_handler
from app.routers import product, category, user

app = FastAPI(title="Storely API", version="1.0.0")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(category.router)
app.include_router(product.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Storely API ishlamoqda"}
```

## 4. Sinash — validatsiya xatosi

```
POST /products/
{"name": "Test", "price": "bu-son-emas", "category_id": 1}
```

Endi javob **izchil formatda**:
```json
{
  "detail": "Validatsiya xatosi",
  "errors": [
    {"field": "price", "message": "Input should be a valid number"}
  ]
}
```

## 5. CORS nima va nega kerak?

**CORS (Cross-Origin Resource Sharing)** — brauzerning xavfsizlik
mexanizmi. Agar frontend (masalan `http://localhost:3000`da ishlaydigan
React ilova) backend'ga (`http://localhost:8000`) so'rov yubormoqchi
bo'lsa — bular **turli origin** (domen+port kombinatsiyasi) hisoblanadi,
va brauzer **default holda bu so'rovni bloklaydi**, agar server
maxsus ruxsat headerlarini qaytarmasa.

**Django solishtirma:** Bu — `django-cors-headers` kutubxonasining
FastAPI'dagi **o'rnatilgan** (built-in) ekvivalenti — alohida kutubxona
kerak emas, FastAPI/Starlette buni o'zida olib yuradi.

## 6. `CORSMiddleware` sozlash

```python
# app/main.py ichiga qo'shiladi
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",   # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Har bir parametr nima qiladi:**
- **`allow_origins`** — qaysi domenlardan so'rov qabul qilinadi. **Productionda
  hech qachon `["*"]` (hammaga ruxsat) ishlatmang**, agar `allow_credentials=True`
  bo'lsa — bu ikkalasi birga xavfsizlik muammosi tug'diradi (brauzer buni
  hatto rad etadi)
- **`allow_credentials`** — cookie yoki `Authorization` headerini
  yuborishga ruxsat berish
- **`allow_methods`** — qaysi HTTP metodlar (`GET`, `POST`, va h.k.)
  ruxsat etilgan
- **`allow_headers`** — qaysi headerlar (masalan `Authorization`,
  `Content-Type`) yuborilishi mumkin

**MUHIM TARTIB QOIDASI:** `CORSMiddleware` — **eng oxirida** qo'shilishi
tavsiya etiladi (yoki hech bo'lmasa, boshqa middleware'lardan oldin emas),
chunki middleware'lar **teskari tartibda** ishlaydi (oxirgi qo'shilgan —
birinchi ishga tushadi).

## 7. Productionga tayyorgarlik — `.env` orqali sozlash

```python
# app/core/config.py — kengaytiriladi
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
```

Bu — hozircha **faqat bilish uchun**, real `.env` integratsiyasi
Dars 27-28'da (Docker, Deployment) to'liq amalga oshiriladi.

## 8. Sinash — CORS

Buni to'liq sinash uchun haqiqiy frontend kerak, lekin oddiy tekshiruv:

```powershell
curl -X OPTIONS http://127.0.0.1:8000/products/ -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" -v
```

Javobda `Access-Control-Allow-Origin: http://localhost:3000` headeri
ko'rinishi kerak.

## Xulosa

- **Global exception handler** — barcha xatolarni izchil formatda
  qaytarish, ichki xato tafsilotlarini oshkor qilmaslik
- **`RequestValidationError`** — Pydantic validatsiya xatolarini
  chiroyli formatga keltirish uchun alohida ushlanadi
- **`Exception`** (umumiy) — kutilmagan xatolarni `500` bilan yashirish
- **`CORSMiddleware`** — frontend bilan ishlash uchun majburiy,
  productionda **hech qachon** `allow_origins=["*"]` + `allow_credentials=True`
  birga ishlatilmaydi
- Bu — **06: Authentication** bo'limining so'nggi darsi — keyingi
  bo'lim (07: Architecture) kodni yanada tuzilishli qilishga qaratilgan

## Amaliy struktura

```
dars-22-exception-handling-cors/
├── README.md
├── requirements.txt
├── alembic.ini
├── alembic/
├── tests/
│   └── (eski testlar + test_exceptions.py YANGI)
└── app/
    ├── core/
    │   ├── security.py
    │   ├── dependencies.py
    │   └── exceptions.py       <- YANGI
    └── main.py                   <- YANGILANADI (handlerlar + CORS qo'shiladi)
```