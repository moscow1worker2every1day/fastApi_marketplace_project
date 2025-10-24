from pydantic import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # app/
ENV_PATH = BASE_DIR.parent


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ENV_PATH / ".env"  #путь к .env
        env_file_encoding = "utf-8"
        extra = "allow"

settings = Settings()
