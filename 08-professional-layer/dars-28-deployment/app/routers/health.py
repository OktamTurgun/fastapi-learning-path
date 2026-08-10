from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as aioredis

from app.database import get_db
from app.core.config import settings
from app.schemas.health import HealthCheckResponse

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])


@router.get("", response_model=HealthCheckResponse, summary="Production Health Check Endpoint")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Production server, PaaS (Render/Railway), load balancerlar uchun
    tizim sog'lig'ini (Database, Redis, App) tekshiradigan endpoint.
    """
    db_status = "unhealthy"
    redis_status = "unhealthy"
    overall_status = "healthy"
    status_code = status.HTTP_200_OK

    # 1. Database connection check
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # 2. Redis connection check
    try:
        r = aioredis.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
        if await r.ping():
            redis_status = "connected"
        await r.close()
    except Exception:
        # Development / test muhitida Redis bo'lmasligi mumkin
        redis_status = "disconnected"

    response_data = {
        "status": overall_status,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "database": db_status,
        "redis": redis_status,
        "details": {
            "debug_mode": settings.DEBUG,
            "project_name": settings.PROJECT_NAME
        }
    }

    return JSONResponse(status_code=status_code, content=response_data)
