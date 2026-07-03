# Dars 03 — FastAPI Project yaratish

## 1. Minimal FastAPI ilova

FastAPI ilovasini yaratish uchun kerak bo'lgan minimal kod atigi 4 qator:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Salom Dunyo!"}
```

Bu yerda `app` — ASGI application obyekti. Uvicorn aynan shu obyektni
qidiradi va ishga tushiradi.

## 2. `FastAPI()` konstruktor parametrlari

`FastAPI()` chaqirilganda bir nechta foydali parametr berish mumkin —
ular avtomatik Swagger/ReDoc sahifalarida ko'rinadi:

```python
app = FastAPI(
    title="Mening API'im",
    description="Bu API nimalar qila oladi haqida tavsif",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI manzili (default: /docs)
    redoc_url="/redoc",     # ReDoc manzili (default: /redoc)
    openapi_url="/openapi.json",  # OpenAPI schema manzili
)
```

**Muhim:** Production'da ba'zida `docs_url=None, redoc_url=None` qilib
dokumentatsiyani butunlay o'chirib qo'yishadi (xavfsizlik uchun, tashqi
foydalanuvchilar API strukturasini ko'rmasin deb).

## 3. Uvicorn buyruqlari va flag'lari

```bash
uvicorn main:app --reload
```

Bu buyruq qismlarga bo'linadi:
- `main` — `main.py` fayli (modul nomi, `.py` siz)
- `app` — o'sha fayl ichidagi `FastAPI()` obyekti nomi
- `--reload` — kod o'zgarganda serverni avtomatik qayta ishga tushiradi
  (**faqat development uchun**, production'da ishlatilmaydi — sekinlashtiradi)

### Foydali qo'shimcha flag'lar

| Flag | Vazifasi | Misol |
|---|---|---|
| `--host` | Qaysi IP'da tinglash | `--host 0.0.0.0` (tashqi qurilmalardan ham kirish uchun) |
| `--port` | Qaysi port'da ishlashi | `--port 8080` |
| `--workers` | Nechta parallel process | `--workers 4` (production, `--reload` bilan birga ishlamaydi) |
| `--log-level` | Log darajasi | `--log-level debug` |

```bash
# Development (standart)
uvicorn main:app --reload

# Tarmoqdagi boshqa qurilmalardan kirish uchun (masalan telefon orqali test)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production'ga yaqinroq (worker'lar bilan, reload'siz)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Django tajribangiz bilan solishtirish:** Django'da `python manage.py
runserver 0.0.0.0:8000` deb yozgansiz — bu yerda mantiq bir xil, faqat
buyruq boshqacha.

## 4. Swagger UI (`/docs`) bilan ishlash

Swagger UI — FastAPI avtomatik generatsiya qiladigan **interaktiv**
dokumentatsiya. `http://127.0.0.1:8000/docs` manzilida ochiladi.

Imkoniyatlari:
- Har bir endpoint uchun **"Try it out"** tugmasi — brauzerdan to'g'ridan-to'g'ri
  so'rov yuborish mumkin (Postman kerak emas)
- Request/response schema'larni ko'rish
- Query/path parametrlarni to'ldirish uchun forma
- Status kodlari va xato javoblarini ko'rish

Bu **Django DRF'dagi Browsable API**'ga o'xshaydi, lekin ancha kuchliroq va
avtomatik — hech qanday qo'shimcha sozlash kerak emas.

## 5. ReDoc (`/redoc`) bilan ishlash

ReDoc — Swagger'ga muqobil, faqat **o'qish uchun** (interaktiv emas)
dokumentatsiya ko'rinishi. `http://127.0.0.1:8000/redoc` manzilida.

Farqi:
- Swagger — interaktiv, sinab ko'rish mumkin, developer uchun qulay
- ReDoc — chiroyli, uzun tavsiflar uchun yaxshi o'qiladi, ko'pincha
  **tashqi hujjat sifatida** (masalan mijozlarga yuborish uchun) ishlatiladi

## 6. OpenAPI schema

Ikkala dokumentatsiya (`/docs` va `/redoc`) aslida bitta manbadan —
`/openapi.json` dan generatsiya qilinadi. Bu JSON schema butun API
strukturasini (endpointlar, parametrlar, response turlari) tasvirlaydi.

Buni ochib ko'ring: `http://127.0.0.1:8000/openapi.json`

Bu schema orqali frontend developerlar avtomatik TypeScript client
generatsiya qilishlari mumkin (masalan `openapi-typescript-codegen` kabi
vositalar bilan) — bu sizning marionettes.uz loyihangizdagi React/TS
frontend bilan integratsiyada juda foydali bo'lishi mumkin.

## Xulosa

- `FastAPI()` konstruktorida `title`, `description`, `version` berish —
  professional odat
- `uvicorn main:app --reload` — development uchun standart buyruq
- `--host 0.0.0.0` — boshqa qurilmalardan test qilish uchun kerak
- `/docs` — interaktiv sinov uchun, `/redoc` — o'qish uchun
- Hammasi `/openapi.json` schema'sidan avtomatik generatsiya bo'ladi