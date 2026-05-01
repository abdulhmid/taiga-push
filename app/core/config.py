from functools import lru_cache
from typing import List, Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Taiga Push API"
    taiga_url: Optional[str] = None
    taiga_token: Optional[str] = None
    project_id: Optional[str] = None
    debug: bool = False
    allowed_origins: List[str] = ["*"]
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
