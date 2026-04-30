from functools import lru_cache
from typing import List, Optional
from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    app_name: str = "Taiga Push API"
    taiga_url: Optional[AnyHttpUrl] = None
    debug: bool = False
    allowed_origins: List[str] = ["*"]
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
