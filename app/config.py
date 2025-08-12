# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DB_URL: str
    JWT_ALG: str = "RS256"
    ACCESS_EXPIRES_MIN: int = 15
    REFRESH_EXPIRES_DAYS: int = 7
    PRIVATE_KEY_PATH: str | None = "./private.pem"
    PUBLIC_KEY_PATH: str | None = "./public.pem"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
