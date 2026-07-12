"""
Konfiguratsiya haqida ma'lumot beruvchi demo router.
"""

from fastapi import APIRouter, Depends
from app.config import Settings, get_settings

router = APIRouter()

@router.get("/health")
def health(settings: Settings = Depends(get_settings)):
  """
  Sog'liqni tekshirish endpointi.
  """
  return {
    "status": "ok",
    "app_name": settings.app_name,
    "debug": settings.debug,
    "max_tasks_per_user": settings.max_tasks_per_user,
    "access_token_expire_minutes": settings.access_token_expire_minutes,
    # admin_email va secret_key MAXFIY — hech qachon qaytarilmaydi!
  }