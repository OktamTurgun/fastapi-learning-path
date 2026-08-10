import os
from typing import List
from pydantic import Field
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Fallback if pydantic-settings is missing in environment
    from pydantic import BaseModel as BaseSettings  # type: ignore
    SettingsConfigDict = None  # type: ignore


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

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
            case_sensitive=True,
        )


settings = Settings()
