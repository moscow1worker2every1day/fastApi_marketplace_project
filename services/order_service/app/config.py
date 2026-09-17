import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import DEFAULT_ENV_FILE, REQUEST_LOG_FORMAT
from app.utils import _get_project_directory


ENV_FILE = os.getenv("APP_ENV_FILE", DEFAULT_ENV_FILE)
PROJECT_ROOT = _get_project_directory()


class AppSettings(BaseSettings):
    app_name: str = Field(
        alias="COMPOSE_PROJECT_NAME",
        default="order-service",
    )
    host: str = Field(
        alias="APP_HOST",
        default="0.0.0.0",
    )
    port: int = Field(
        alias="APP_INTERNAL_PORT",
        default=8003,
    )
    version: str = Field(
        alias="DEPLOY_VERSION",
        default="unknown",
    )

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
    )


class PostgresSettings(BaseSettings):
    user: str = Field(
        alias="POSTGRES_USER",
        default="postgres",
    )
    password: str = Field(
        alias="POSTGRES_PASSWORD",
        default="postgres",
    )
    host: str = Field(
        alias="POSTGRES_HOST",
        default="host.docker.internal",
    )
    port: int = Field(
        alias="POSTGRES_PORT",
        default=5432,
    )
    database: str = Field(
        alias="POSTGRES_DB",
        default="postgres",
    )

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
    )

    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    @property
    def sync_database_url(self):
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class AlembicSettings(BaseSettings):
    alembic_path: str = Field(
        alias="ALEMBIC_PATH",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic/"),
    )
    alembic_ini_path: str = Field(
        alias="ALEMBIC_INI_PATH",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"),
    )
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
    )


class LoguruSettings(BaseSettings):
    logs_dir: str = Field(
        alias="LOGURU_LOGS_DIR",
        default="logs",
    )
    log_level: str = Field(
        alias="LOGURU_LOG_LEVEL",
        default="DEBUG",
    )
    rotation: str = Field(
        alias="LOGURU_ROTATION",
        default="100 MB",
    )
    retention: str = Field(
        alias="LOGURU_RETENTION",
        default="10 days",
    )
    encoding: str = Field(
        alias="LOGURU_ENCODING",
        default="utf-8",
    )
    log_format: str = Field(
        alias="LOGURU_LOG_FORMAT",
        default=REQUEST_LOG_FORMAT,
    )
    order_log_name: str = Field(
        alias="LOGURU_ORDER_LOG_NAME",
        default="order.log",
    )
    slow_requests_log_name: str = Field(
        alias="LOGURU_SLOW_REQUESTS_LOG_NAME",
        default="slow_requests.log",
    )
    errors_log_name: str = Field(
        alias="LOGURU_ERRORS_LOG_NAME",
        default="errors.log",
    )
    startup_log_name: str = Field(
        alias="LOGURU_STARTUP_LOG_NAME",
        default="startup.log",
    )

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
    )

class Settings:
    def __init__(
        self,
        app: AppSettings,
        postgres: PostgresSettings,
        alembic: AlembicSettings,
        loguru: LoguruSettings,
    ):
        self.app = app
        self.postgres = postgres
        self.alembic = alembic
        self.loguru = loguru

settings = Settings(
    app=AppSettings(),
    postgres=PostgresSettings(),
    alembic=AlembicSettings(),
    loguru=LoguruSettings(),
)
