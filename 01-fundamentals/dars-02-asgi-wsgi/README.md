# Dars 02 — ASGI va WSGI nima?

## 1. Muammo nimada edi?

Python web dunyosida serverlar bilan framework'lar (Django, Flask, FastAPI)
o'rtasida "til" kerak — ya'ni server so'rovni qanday formatda framework'ga
uzatishi, framework javobni qanday qaytarishi kelishilgan bo'lishi kerak.
Aynan shu "til" (interfeys/protokol) — WSGI va ASGI.

## 2. WSGI nima?

**WSGI** — Web Server Gateway Interface. 2003-yilda standartlashtirilgan,
Python web dunyosining birinchi umumiy interfeysi.

- Django (an'anaviy), Flask shu asosda ishlaydi
- **Faqat sinxron (sync)** — bir vaqtning o'zida bitta so'rovni to'liq
  qayta ishlab bo'lgach, keyingisiga o'tadi
- Server: Gunicorn, uWSGI

**Muammo:** Agar bitta so'rov DB yoki tashqi API'ni kutayotgan bo'lsa
(I/O-bound), worker process shu vaqt band bo'lib turadi — boshqa so'rovlarni
qabul qila olmaydi (agar ko'p worker/thread ishlatilmasa).

## 3. ASGI nima?

**ASGI** — Asynchronous Server Gateway Interface. WSGI'ning "keyingi avlodi"
sifatida 2016-yilda yaratilgan (Django jamoasi tomonidan boshlangan loyiha).

- FastAPI, Starlette, Django (Channels/async views) shu asosda ishlaydi
- **Sinxron VA asinxron** ikkalasini ham qo'llab-quvvatlaydi
- Bitta process ko'p so'rovni **bir vaqtda** (concurrent) ushlab turishi
  mumkin — I/O kutish vaqtida (masalan DB so'rovi) boshqa so'rovni qayta
  ishlay oladi
- WebSocket, Server-Sent Events kabi "uzoq umr ko'radigan" ulanishlarni
  ham qo'llab-quvvatlaydi (WSGI buni umuman qila olmaydi)

## 4. WSGI vs ASGI — solishtirish

| | WSGI | ASGI |
|---|---|---|
| Turi | Faqat sync | Sync + Async |
| Concurrency | Thread/Process orqali | Event loop orqali (asyncio) |
| WebSocket | ❌ Yo'q | ✅ Bor |
| Ishlatuvchi framework | Django (classic), Flask | FastAPI, Starlette |
| Server | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |
| I/O-bound ishlarda | Sekinroq (worker band bo'ladi) | Tezroq (event loop band bo'lmaydi) |

**Django DRF tajribangizga bog'lab tushuntirish:** Django odatiy holda WSGI
orqali ishlaydi (`manage.py runserver` ostida ham). Shu sababli DRF'da
`def view(request):` sync yozilgan bo'lardi. FastAPI'da esa `async def`
yozish imkoniyati bor, chunki asos ASGI.

## 5. Uvicorn nima?

**Uvicorn** — Python uchun eng mashhur ASGI server. FastAPI hujjatlarida
standart tavsiya etiladigan server.

- `uvloop` asosida ishlaydi (asyncio'ning tezlashtirilgan versiyasi)
- Development uchun `--reload` flag bilan avtomatik qayta ishga tushadi
- Production uchun ko'pincha **Gunicorn + Uvicorn workers** birga
  ishlatiladi (Gunicorn process menejer sifatida, Uvicorn ishchi sifatida)

```bash
uvicorn main:app --reload          # development
uvicorn main:app --workers 4       # production (4 ta parallel process)
```

## 6. Hypercorn nima?

**Hypercorn** — Uvicorn'ga muqobil ASGI server. Farqi:

- HTTP/2 va HTTP/3'ni ham qo'llab-quvvatlaydi (Uvicorn asosan HTTP/1.1)
- Trio va asyncio ikkalasini ham qo'llaydi
- Amalda Uvicorn ko'proq ishlatiladi, lekin HTTP/2 kerak bo'lganda Hypercorn
  tanlanadi

```bash
pip install hypercorn
hypercorn main:app --reload
```

## 7. Request Lifecycle — so'rov qanday yo'l bosadi?

1. Client (brauzer/Postman) → HTTP so'rov yuboradi
↓
2. Uvicorn (ASGI server) → so'rovni qabul qiladi, ASGI formatiga o'giradi
↓
3. Starlette (FastAPI asosi) → routing: qaysi endpoint'ga tegishli ekanini aniqlaydi
↓
4. Middleware'lar → so'rov middleware zanjiridan o'tadi (CORS, logging va h.k.)
↓
5. Dependency Injection → Depends() orqali kerakli obyektlar tayyorlanadi
↓
6. Pydantic validatsiya → request body/query/path parametrlar tekshiriladi
↓
7. Sizning endpoint funksiyangiz ishga tushadi (business logic)
↓
8. Response Pydantic model orqali serializatsiya qilinadi
↓
9. Middleware'lar (javob yo'nalishida qayta ishlaydi)
↓
10. Uvicorn → javobni HTTP formatida clientga qaytaradi
 
Bu zanjirni tushunish juda muhim — masalan, agar keyinchalik middleware yoki
exception handler yozsangiz, aynan shu bosqichlarning qaysi birida
ishlayotganingizni bilishingiz kerak bo'ladi.

## Xulosa

- WSGI = eski, faqat sync, Django classic/Flask
- ASGI = yangi, sync+async, FastAPI/Starlette
- Uvicorn = eng ko'p ishlatiladigan ASGI server
- Request lifecycle'ni bilish — middleware, DI, exception handling'ni
  tushunish uchun poydevor