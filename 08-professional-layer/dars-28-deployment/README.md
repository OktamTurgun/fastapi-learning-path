# Dars 28 — Deployment (Storely API Production Readiness & Cloud)

Hozirgacha biz FastAPI ilovamizni o'z noutbukimizda `uvicorn app.main:app --reload` buyrug'i bilan ishga tushirib keldik va Dars 27 da uni Docker konteyneriga joylashtirishni o'rgandik. 

Lekin real foydalanuvchilar kirishi va ilovamiz 24/7 uzluksiz ishlashi uchun uni **Production (ishchi) muhitiga deploy qilish** va **bulutli serverlarga (Render, Railway, VPS)** joylashtirishimiz kerak.

Ushbu darsda biz FastAPI loyihasini noldan professional **Production-Ready** holatiga keltirishni va real bulutli platformalarga joylashtirishni ko'rib chiqamiz.

---

## 1. Development vs Production Muhitlari

Lokal kompyuterda dasturlash (Development) va real serverda ishlash (Production) o'rtasida tubdan farqlar mavjud:

| Xususiyat | Development (Lokal) | Production (Server) |
|---|---|---|
| **Server** | `uvicorn --reload` (bitta jarayon) | `Gunicorn` + multi-worker `UvicornWorker` |
| **Kod o'zgarishi** | Avtomatik qayta yuklanadi (`--reload`) | Qayta yuklanmaydi, barqaror konteyner ishlaydi |
| **Baza (Database)** | SQLite (`storely.db`) | PostgreSQL / Cloud Database |
| **Xatoliklar (Debug)** | `DEBUG=True`, to'liq stack trace ko'rinadi | `DEBUG=False`, xavfsiz va umumiy JSON xabarlar |
| **CORS** | `allow_origins=["*"]` (hamma ruxsat berilgan) | Aniq ruxsat etilgan domenlar (`https://myfrontend.com`) |
| **Monitoting** | Terminal konsol loglari | Health Check endpoints, Cloud Logs (Cloudwatch/Render) |

---

## 2. Dynamic Configuration Management (`pydantic-settings` & `.env`)

Production muhitida **hech qachon secret kalitlar va baza parollarini kod ichida hardcode qilmaslik** kerak. Barcha konfiguratsiyalar Muhit o'zgaruvchilari (`Environment Variables`) orqali boshqariladi.

FastAPI'da buni eng qulay va xavfsiz usuli — `pydantic-settings` kutubxonasidagi `BaseSettings` sinfidir.

### `app/core/config.py` kodi:

```python
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Storely API"
    ENVIRONMENT: str = Field(default="development")  # development, production, testing
    DEBUG: bool = Field(default=True)
    
    # Security
    SECRET_KEY: str = Field(default="super-secret-key-change-this-in-production-1234567890")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # Database & Redis
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./storely.db")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:8000"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

### Production `.env` fayli namunasi:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=e8f921a8809c488349ab9c18274d11094022a
DATABASE_URL=postgresql+asyncpg://storely_user:strong_password@db-host:5432/storely_db
CELERY_BROKER_URL=rediss://default:password@redis-host:6379/0
ALLOWED_ORIGINS=["https://storely.uz", "https://admin.storely.uz"]
```

---

## 3. Production Server Architecture: Gunicorn + UvicornWorker

Nega productionda faqat `uvicorn main:app` ishlatilmaydi?
- `Uvicorn` — bu juda tezkor **ASGI server** (bitta CPU yadroda bitta event loop yurgizadi).
- `Gunicorn` — bu professional **Process Manager** (ishchi jarayonlarni nazorat qiladi, bittasi qulasa qayta tiriltiradi, CPU'ning barcha yadro (core)lariga yuklamani teng bo'ladi).

Productionda ularning **kombinatsiyasi** ishlatiladi: Gunicorn boshqaruvchi sifatida bir nechta Uvicorn workerlarini boshqaradi.

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

**Bayroqlar tushuntirishi:**
- `-w 4` — 4 ta alohida worker (jarayon) ochadi. (Formula: `2 * CPU_CORES + 1`).
- `-k uvicorn.workers.UvicornWorker` — Gunicorn'ga Uvicorn'ning asinxron worker sinfidan foydalanishni aytadi.
- `--bind 0.0.0.0:8000` — Server barcha tarmog' interfeyslarining 8000-portida tinglaydi.

---

## 4. Health Check Endpoint (`GET /health`)

Production serverlarda Load Balancerlar va Bulutli platformalar (Render, Railway, Kubernetes) ilova tirikligini va so'rov qabul qilishga tayyorligini tekshirish uchun har necha soniyada **Health Check** yuboradi.

Biz `GET /health` endpointini yaratamiz, u nafaqat FastAPI javob berishini, balki **Ma'lumotlar bazasi** va **Redis** serveriga ulanish ishlayotganini tekshiradi:

### `app/routers/health.py`:

```python
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis

from app.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "unhealthy"
    redis_status = "unhealthy"
    overall_status = "healthy"
    status_code = status.HTTP_200_OK

    # 1. Database ulanishini tekshirish
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # 2. Redis ulanishini tekshirish
    try:
        r = aioredis.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
        if await r.ping():
            redis_status = "connected"
        await r.close()
    except Exception:
        redis_status = "disconnected"

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "database": db_status,
            "redis": redis_status,
        }
    )
```

---

## 5. Production-Ready Docker & Migration Script (`start.sh`)

Production uchun Dockerfile tuzishda **xavfsizlik (Security)** va **avtomatlashtirish (Automated Migrations)** muhim o'rin tutadi.

### 1. `start.sh` (Startup Script):

Server ishga tushganda avval Alembic migratsiyalarini avtomatik yurgazadi, so'ng Gunicorn'ni ishga tushiradi:

```bash
#!/bin/sh
set -e

echo "=== [PRODUCTION STARTUP] ==="
echo "1. Migratsiyalarni yurgizish (Alembic)..."
alembic upgrade head

echo "2. Gunicorn serverini ishga tushirish..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### 2. Production `Dockerfile`:

```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Root bo'lmagan foydalanuvchi yaratish (Security Best Practice)
RUN addgroup --system appuser && adduser --system --group appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . $APP_HOME

RUN chmod +x ./start.sh && chown -R appuser:appuser $APP_HOME

USER appuser

EXPOSE 8000

CMD ["./start.sh"]
```

---

## 6. Deployment Platformalariga Joylashtirish Yo'riqnomalari

### A) Render.com (PaaS Blueprint bilan)

Render platformasida Infrastructure-as-Code prinsipida `render.yaml` orqali FastAPI Web Service, PostgreSQL va Redis xizmatlarini bitta fayl bilan yaratish mumkin:

`render.yaml`:
```yaml
services:
  - type: web
    name: storely-api
    env: docker
    dockerfilePath: ./Dockerfile
    healthCheckPath: /health
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: "False"
      - key: DATABASE_URL
        fromDatabase:
          name: storely-db
          property: connectionString

databases:
  - name: storely-db
    databaseName: storely
    user: storely_user
```

### B) VPS / Cloud Server (Ubuntu + Nginx + Gunicorn)

Agar o'zingizning Ubuntu VPS (masalan Oracle Cloud yoki DigitalOcean) serveringiz bo'lsa:

1. **Systemd Service (`/etc/systemd/system/storely.service`)**:
   ```ini
   [Unit]
   Description=Storely FastAPI Production Service
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/fastapi-learning-path/08-professional-layer/dars-28-deployment
   ExecStart=/home/ubuntu/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Nginx Reverse Proxy (`/etc/nginx/sites-available/storely`)**:
   ```nginx
   server {
       server_name api.storely.uz;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **HTTPS SSL olish (Certbot)**:
   ```bash
   sudo certbot --nginx -d api.storely.uz
   ```

---

## 7. CI/CD Pipeline Basics (GitHub Actions)

Kodingizni GitHub'ga push qilganingizda, xatolar serverga yetib bormasligi uchun **Continuous Integration (CI)** avtomatik pytest'ni yurgizishi kerak.

`.github/workflows/ci.yml`:
```yaml
name: FastAPI Production CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.13'
    - run: pip install -r 08-professional-layer/dars-28-deployment/requirements.txt
    - run: pytest 08-professional-layer/dars-28-deployment/tests
```

---

## 8. Django Deployment va FastAPI Deployment Solishtirmasi

| Mezon | Django Deployment | FastAPI Deployment |
|---|---|---|
| **Interfeys standarti** | WSGI (yoki Asgi Channels uchun) | ASGI (Tug'ma Asinxron) |
| **WSGI/ASGI Server** | Gunicorn (`gunicorn myproject.wsgi:application`) | Gunicorn + UvicornWorker (`gunicorn -k uvicorn.workers.UvicornWorker app.main:app`) |
| **Baza drayveri (Database Driver)** | `psycopg2` (sinchron) | `asyncpg` (`postgresql+asyncpg://`) |
| **Static fayllar** | `python manage.py collectstatic` + WhiteNoise/Nginx | FastAPI'da API birinchi darajali, Front-end ko'pincha alohida React/Next.js/S3 da |
| **Migratsiya** | `python manage.py migrate` | `alembic upgrade head` (`start.sh` ichida) |

---

## Xulosa

- Production muhitida `uvicorn --reload` ishlatilmaydi; uning o'rniga **Gunicorn + UvicornWorker** ishlatiladi.
- Konfiguratsiyalar va secretlar **`pydantic-settings`** orqali `.env` va muhit o'zgaruvchilaridan olinadi.
- **`/health`** endpointi server va tashqi xizmatlar (DB, Redis) holatini kuzatish uchun shart.
- **`start.sh`** skripti konteyner ishga tushishi bilan bazani **Alembic** orqali avtomatik migratsiya qiladi.
- **GitHub Actions** CI/CD pipeline'i koddagi xatoliklarni deploy'dan avval tutib qoladi.

---

## Amaliy Mashq

`exercise/exercise.py` faylini oching va `/health/liveness` hamda `/health/readiness` endpointlarini Kubernetes/Cloud standarti bo'yicha to'liq ishga tushiring.

Sinash uchun:
```bash
pytest 08-professional-layer/dars-28-deployment/tests
```
