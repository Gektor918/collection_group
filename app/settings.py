import os

from pydantic_settings import BaseSettings, SettingsConfigDict


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://cms:cms@localhost:5432/cms")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "media")
TYPE_POINT_CMS = "cms"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://cms:cms@localhost:5432/cms"
    media_root: str = "./media"
    logs_path: str = "./logs"
    media_url: str = "/media"
    image_max_side: int = 512
    origins: list[str] = ["http://localhost:8000"]
    debug: bool = True

settings = Settings()

origins = settings.origins
media_root = settings.media_root
media_url = settings.media_url
logs_path = settings.logs_path
image_max_side = settings.image_max_side
database_url = settings.database_url
debug = settings.debug
