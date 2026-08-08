# Dars 27 — Docker (Storely)

Hozirgacha loyihani ishga tushirish uchun **bir nechta alohida narsa**
kerak edi: Python virtual muhit, `pip install`, Redis (Docker orqali
qo'lda), Celery worker (alohida terminal), uvicorn (yana alohida
terminal). Bu — sizning kompyuteringizda ishlaydi, lekin boshqa birov
(yoki production server) buni ishga tushirish uchun xuddi shu
qadamlarni takrorlashi kerak — bu esa xatolarga to'la jarayon.
**Docker** — shu muammoni hal qiladi: butun ilova (kodi, kutubxonalari,
muhiti) bitta "konteyner" ichiga o'raladi, va u har qanday joyda bir
xil ishlaydi.

## 1. Nega Docker kerak — muammoning o'zi

"Mening kompyuterimda ishlayapti" — bu dasturchilar orasida eng
mashhur muammo. Sabab: sizning Python versiyangiz, o'rnatilgan
kutubxonalar, operatsion tizim sozlamalari — boshqa kompyuterda farq
qilishi mumkin. Docker bu farqlarni yo'q qiladi — konteyner ichida
**aynan bir xil muhit** bo'ladi, qayerda ishga tushirilishidan qat'i
nazar (sizning noutbukingiz, hamkasbingiz kompyuteri, yoki bulutdagi
server).

**Siz bu bilan allaqachon tanishsiz** — marionettes.uz'ni Oracle
Cloud'ga joylashtirishda, EduCore CRM'ni Render'ga deploy qilishda
Docker'dan foydalangansiz. Bugun buni FastAPI + Celery + Redis
kontekstida tizimli qilib ko'rib chiqamiz.

## 2. Image vs Container — asosiy tushunchalar

| Tushuncha | Ma'nosi | O'xshashi |
|---|---|---|
| **Image (obraz)** | "Retsept" — qanday qilib konteyner qurish kerakligi haqidagi ko'rsatma | Klass (`class`) |
| **Container (konteyner)** | Image'dan yaratilgan, ishlab turgan nusxa | Obyekt (`instance`) |
| **Dockerfile** | Image'ni qurish uchun ko'rsatmalar fayli | `class` ta'rifi |

Siz avval `docker run -d -p 6379:6379 redis` yozganingizda — `redis`
bu **image** (Docker Hub'dan yuklab olingan tayyor "retsept"), va bu
buyruq shu image'dan **container** yaratdi.

## 3. `Dockerfile` — o'zimizning ilovamizni qadoqlash

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Har bir qatorni tushuntiramiz:**

- `FROM python:3.13-slim` — boshlang'ich image (allaqachon Python
  3.13 o'rnatilgan, "slim" — engil versiya, kerak bo'lmagan narsalar
  yo'q)
- `WORKDIR /app` — konteyner ichida ishchi papka (barcha keyingi
  buyruqlar shu yerdan ishlaydi)
- `COPY requirements.txt .` — **avval faqat** `requirements.txt`ni
  nusxalash (butun kodni emas!) — bu muhim optimallashtirish: agar
  keyinchalik faqat kod o'zgarsa (kutubxonalar emas), Docker `pip
  install` qatorini qayta bajarmaydi (keshlaydi), qurish tezlashadi
- `RUN pip install ...` — kutubxonalarni o'rnatish
- `COPY . .` — qolgan barcha kodni nusxalash
- `EXPOSE 8000` — bu konteyner qaysi portda "tinglashini"
  hujjatlashtiradi (majburiy emas, lekin yaxshi amaliyot)
- `CMD [...]` — konteyner ishga tushganda bajariladigan buyruq

**Django solishtirma:** bu — sizning marionettes.uz'ni Oracle Cloud'ga
joylashtirganingizda yozgan `Dockerfile`ingiz bilan deyarli bir xil
tuzilma, faqat `manage.py runserver` o'rniga `uvicorn` bor.

## 4. `.dockerignore` — keraksiz fayllarni chiqarib tashlash

```
# .dockerignore
venv/
__pycache__/
*.pyc
.git/
.pytest_cache/
*.db
.env
tests/
```

Bu — `.gitignore`ga o'xshaydi, lekin Git uchun emas, Docker uchun:
image qurilganda bu fayllar konteynerga **nusxalanmaydi**, image
hajmi kichikroq bo'ladi va qurish tezroq ishlaydi.

## 5. `docker-compose.yml` — bir nechta xizmatni birga boshqarish

Bizning Storely'da **uchta** narsa bir vaqtda ishlashi kerak: FastAPI
server, Redis, Celery worker. Buларni qo'lda uchta alohida terminalda
ishga tushirish o'rniga, `docker-compose` bularning barchasini
**bitta buyruq bilan** boshqaradi:

```yaml
# docker-compose.yml
version: "3.9"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: .
    command: celery -A app.celery_app worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
```

**Tushuntirish:**

- `services:` — ostida har biri alohida konteyner bo'ladigan
  xizmatlar ro'yxati
- `web:` — bizning FastAPI ilovamiz. `build: .` — shu papkadagi
  `Dockerfile`dan image quriladi
- `redis:` — tayyor Docker Hub image'i ishlatiladi (`build` kerak
  emas)
- `celery_worker:` — **xuddi shu image'dan** (`build: .`), lekin
  **boshqa buyruq** (`command:`) bilan ishga tushiriladi — bu muhim
  tushuncha: bir xil kod, ikki xil rol (bittasi HTTP server,
  ikkinchisi Celery worker)
- `depends_on:` — "bu xizmat boshqasidan keyin ishga tushsin" (lekin
  bu faqat **tartibni**, "tayyor bo'lishini" kafolatlamaydi — bu
  muhim nozik joy, ba'zan qo'shimcha "healthcheck" kerak bo'ladi)
- `volumes: - .:/app` — xost kompyuterdagi joriy papkani konteyner
  ichidagi `/app`ga bog'laydi, shunda **kodni o'zgartirganda
  konteynerni qayta qurish shart emas** (development uchun juda
  qulay)

**Muhim — Windows'dagi `--pool=solo` muammosi bu yerda ham
dolzarb:** Linux-asosli Docker konteyner ichida Celery worker ishga
tushirilganda, **`--pool=solo` kerak emas** — chunki konteyner ichida
har doim Linux muhiti (hatto sizning host tizimingiz Windows bo'lsa
ham, Docker konteynerlari Linux yadrosida ishlaydi). Bu — Docker'ning
yana bir amaliy foydasi: Windows-specific muammolar konteyner ichida
yo'qoladi.

## 6. `redis://redis:6379/0` — nega `localhost` emas?

Diqqat qiling: `docker-compose.yml`da broker manzili
`redis://redis:6379/0`, `localhost:6379` emas. Sabab: `docker-compose`
tarmog'ida har bir xizmat o'z **nomi** orqali murojaat qilinadi (bu —
ichki DNS kabi ishlaydi). `web` konteyneri ichidan turib, Redis'ga
ulanish uchun `redis` (xizmat nomi) ishlatiladi, `localhost` emas —
chunki `localhost` konteyner ichida **o'zining** ichki tarmog'iga
ishora qiladi, boshqa konteynerga emas.

Bu — sizning `app/celery_app.py`dagi hardcoded
`"redis://localhost:6379/0"`ni **muhit o'zgaruvchisi** orqali
o'qiladigan qilib o'zgartirishni talab qiladi:

```python
# app/celery_app.py — yangilanadi
import os
from celery import Celery

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "storely",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"],
)
```

`os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")` — agar
`CELERY_BROKER_URL` muhit o'zgaruvchisi berilgan bo'lsa (Docker
ichida, `docker-compose.yml`dagi `environment:` orqali) o'shani
ishlatadi, aks holda (lokal, Docker'siz ishga tushirilganda)
`localhost`ga qaytadi. Bu — **ikkala muhitda ham** (Docker bilan va
Docker'siz) ishlashni ta'minlaydi.

## 7. Ishga tushirish buyruqlari

```powershell
# Barcha xizmatlarni qurish va ishga tushirish
docker-compose up --build

# Fonda ishga tushirish
docker-compose up -d

# To'xtatish
docker-compose down

# Loglarni ko'rish (masalan faqat celery_worker'niki)
docker-compose logs -f celery_worker
```

## 8. Django bilan solishtirma

Sizning marionettes.uz/theater-manager loyihalaringizda
`docker-compose.yml`da odatda `db` (PostgreSQL), `redis`, `web`
(Django), va ba'zan `celery` xizmatlari bo'lgan — bu yerdagi tuzilma
**deyarli bir xil**. Asosiy farq — Django loyihalarda ko'pincha
`gunicorn` ishlatiladi (`CMD`da), bu yerda `uvicorn`.

## Xulosa

- **Image** — retsept, **Container** — ishlayotgan nusxa
- **`Dockerfile`** — o'zimizning ilovani qadoqlash ko'rsatmasi
- **`docker-compose.yml`** — bir nechta xizmatni (web, redis,
  celery_worker) birga boshqarish
- **Xizmat nomi orqali murojaat** (`redis`, `localhost` emas) —
  konteynerlar ichki tarmog'ida
- **Muhit o'zgaruvchilari** (`os.getenv(...)`) — Docker ichida va
  tashqarisida ishlashni moslashtirish uchun
- Windows-specific `--pool=solo` muammosi Docker konteyner ichida
  yo'qoladi

## Amaliy struktura

```
dars-27-docker/
├── README.md
├── Dockerfile          <- YANGI
├── .dockerignore        <- YANGI
├── docker-compose.yml    <- YANGI
└── app/
    └── celery_app.py      <- YANGILANADI (os.getenv orqali)
```