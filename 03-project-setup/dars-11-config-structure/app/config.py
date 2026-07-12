"""
Dars 11 — Konfiguratsiya boshqaruvi
Barcha muhit o'zgaruvchilari shu yerda markazlashtirilgan.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   # .env'da qo'shimcha o'zgaruvchi bo'lsa, xato bermasin
    )

    app_name: str = "Storely API"
    debug: bool = False
    database_url: str = "sqlite:///./demo.db"
    secret_key: str = "dev-secret-key-almashtiring"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    """
    Settings obyektini bir marta yaratib, keshda saqlaydi.
    Har safar Depends(get_settings) chaqirilganda .env qayta o'qilmaydi.
    """
    return Settings()