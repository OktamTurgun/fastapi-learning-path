# Dars 01 — FastAPI nima?

## 1. FastAPI nima?

FastAPI — Python uchun zamonaviy, tez (high-performance) web framework bo'lib,
API yaratish uchun mo'ljallangan. U 2018-yilda Sebastián Ramírez tomonidan
yaratilgan va quyidagi narsalarga asoslanadi:

- **Starlette** — ASGI toolkit (routing, middleware, request/response asosi)
- **Pydantic** — data validation va serialization

## 2. Nima uchun FastAPI?

| Xususiyat | Tushuntirish |
|---|---|
| **Tezlik** | Node.js va Go bilan bir qatorda turadigan performance (Starlette + Uvicorn tufayli) |
| **Avtomatik validatsiya** | Pydantic orqali kiruvchi ma'lumotlar avtomatik tekshiriladi |
| **Avtomatik dokumentatsiya** | Swagger UI (`/docs`) va ReDoc (`/redoc`) o'zi generatsiya bo'ladi |
| **Type hints asosida** | Python type hinting orqali IDE'da autocomplete, kamroq xatolik |
| **Async qo'llab-quvvatlash** | `async def` bilan yuqori concurrency |

## 3. Qayerlarda ishlatiladi?

- REST API backendlar (mobil ilova, frontend uchun)
- Microservice arxitektura
- Machine Learning modellarini serve qilish (masalan, OpenAI, Uber, Netflix
  ichki tizimlarida ishlatiladi)
- Real-time tizimlar (WebSocket qo'llab-quvvatlaydi)

## 4. Django REST Framework bilan farqi

| | Django REST Framework | FastAPI |
|---|---|---|
| Asos | Django (full-stack framework) | Starlette (faqat ASGI toolkit) |
| Turi | Sync (asosan) | Async-first |
| Validatsiya | Serializers | Pydantic (type hints orqali) |
| Tezlik | O'rtacha | Yuqori |
| Admin panel | ✅ Bor | ❌ Yo'q (kerak bo'lsa alohida qo'shiladi) |
| ORM | Django ORM (built-in) | Yo'q (SQLAlchemy tashqaridan ulanadi) |
| O'rganish egri chizig'i | Kattaroq (batteries included) | Kichikroq (minimalist) |
| Eng yaxshi holat | To'liq web ilova (admin, auth, ORM birga) | Sof API, mikroservis, yuqori performance kerak bo'lganda |

**Muhim xulosa:** Django DRF "hammasi bir joyda" (batareyalar bilan) keladi,
FastAPI esa "minimalist, lekin kuchli" — siz nimani xohlasangiz, o'shani
qo'shib borasiz (auth, DB, caching — barchasi tashqi kutubxonalar orqali).

## Xulosa

FastAPI — validatsiya, dokumentatsiya va tezlikni birlashtirgan framework.
Siz Django DRF bilan tanish bo'lganingiz uchun, asosiy farq: **DRF sizga
tayyor tuzilma beradi, FastAPI esa erkinlik beradi — lekin bu erkinlik
javobgarlik bilan keladi** (struktura, arxitekturani o'zingiz qurasiz).