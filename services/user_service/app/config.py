from pydantic_settings import BaseSettings, SettingsConfigDict
import enum


class UserRoles(enum.Enum):
    user = "user"
    seller = "seller"
    admin = "admin"


class Settings(BaseSettings):
    MODE: str | None = "TEST"
    APP_NAME: str = "User-Service"

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # database_url_local: str | None = None
    # database_url_docker: str

    rabbitmq_url: str

    jwt_secret_key: str
    jwt_private_key_path: str
    jwt_public_key_path: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
