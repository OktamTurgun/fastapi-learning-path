from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    parcel_base_fee: float = 5000.0       
    parcel_rate_per_kg: float = 2000.0

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()    