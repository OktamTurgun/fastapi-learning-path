# Dars 10 — Mustaqil mashq: Storely — Xodim (Employee) tizimi

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


    app_name: str = "Task Manager API"
    debug: bool = False
    max_tasks_per_user: int = 50
    admin_email: str
    secret_key: str 
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    """
    Settings obyektini bir marta yaratib, keshda saqlaydi.
    Har safar Depends(get_settings) chaqirilganda .env qayta o'qilmaydi.
    """
    return Settings()