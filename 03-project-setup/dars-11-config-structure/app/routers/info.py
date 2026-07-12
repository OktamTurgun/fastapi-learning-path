"""
Konfiguratsiya haqida ma'lumot beruvchi demo router.
"""

from fastapi import APIRouter, Depends
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/config-info")
def config_info(settings: Settings = Depends(get_settings)):
    """
    E'tibor bering: secret_key hech qachon response'da ko'rsatilmaydi —
    bu Dars 10'da o'rgangan response_model tamoyilining davomi.
    """
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "database_url": settings.database_url,
        "access_token_expire_minutes": settings.access_token_expire_minutes,
        # secret_key MAXFIY — hech qachon qaytarilmaydi!
    }