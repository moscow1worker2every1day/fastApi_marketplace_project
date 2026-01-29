from pydantic_settings import BaseSettings, SettingsConfigDict
import enum


class UserRoles(enum.Enum):
    user = "user"
    seller = "seller"
    admin = "admin"


class Settings(BaseSettings):
    app_name: str = "User-Service"
    database_url_local: str | None = None
    database_url_docker: str

    rabbitmq_url: str

    jwt_secret_key: str
    jwt_private_key_path: str
    jwt_public_key_path: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
