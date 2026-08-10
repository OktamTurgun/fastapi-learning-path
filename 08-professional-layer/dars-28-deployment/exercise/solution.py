"""
DARS 28 EXERCISE SOLUTION: Liveness va Readiness Probes
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis

from app.database import get_db
from app.core.config import settings

exercise_router = APIRouter(prefix="/health", tags=["Exercise Health Solution"])


@exercise_router.get("/liveness")
async def liveness_probe():
    """Liveness probe: Server jarayoni faolmi?"""
    return {"status": "alive"}


@exercise_router.get("/readiness")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """Readiness probe: Server trafikni qabul qilishga tayyormi?"""
    is_ready = True
    details = {"db": "ok", "redis": "ok"}

    # DB Check
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        is_ready = False
        details["db"] = f"failed: {str(e)}"

    # Redis Check
    try:
        r = aioredis.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
        await r.ping()
        await r.close()
    except Exception as e:
        is_ready = False
        details["redis"] = f"failed: {str(e)}"

    if is_ready:
        return {"status": "ready", "details": details}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "details": details}
        )
