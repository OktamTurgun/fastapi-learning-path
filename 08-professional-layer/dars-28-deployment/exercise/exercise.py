"""
DARS 28 EXERCISE: Production Readiness & Health Check extension

Vazifa:
FastAPI ilovasida Kubernetes / PaaS (Render, Railway) talablariga mos
Liveness va Readiness probe endpointlarini yaratish:

1. `/health/liveness` (Liveness Probe):
   - Server ishlab turganini (process alive) bildiradi.
   - Tez javob qaytarishi va DB/Redis kabi external dependency'larni kutmasligi kerak.
   - Qaytarishi kerak: {"status": "alive"} va HTTP 200 OK.

2. `/health/readiness` (Readiness Probe):
   - Server so'rovlarni qabul qilishga TAYYORLIGINI tekshiradi (DB ulanishi va Celery status).
   - Agar DB yoki Redis ishlamasa, HTTP 503 Service Unavailable qaytarishi kerak.
   - Qaytarishi kerak: {"status": "ready", "db": "ok", "redis": "ok"} yoki xatolik bilan 503 status code.

Quyidagi `exercise_router`ni to'ldiring:
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Mashqni to'ldirish joyi:
exercise_router = APIRouter(prefix="/health", tags=["Exercise Health"])


@exercise_router.get("/liveness")
async def liveness_probe():
    # TODO: Liveness probe handler'ni yozing
    pass


@exercise_router.get("/readiness")
async def readiness_probe():
    # TODO: Readiness probe handler'ni yozing (DB va Redis ulanishini tekshiring)
    pass
