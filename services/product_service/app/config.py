import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import DEFAULT_ENV_FILE, FILE_LOG_FORMAT, REQUEST_LOG_FORMAT
from app.utils import _get_project_directory


ENV_FILE = os.getenv("APP_ENV_FILE", DEFAULT_ENV_FILE)
PROJECT_ROOT = _get_project_directory()


class AppSettings(BaseSettings):
    app_name: str = Field(
        alias="COMPOSE_PROJECT_NAME",
        default="product-service",
    )
    host: str = Field(
        alias="APP_HOST",
        default="0.0.0.0",
    )
    port: int = Field(
        alias="APP_INTERNAL_PORT",
        default=8001,
    )
    reload: bool = Field(
        alias="APP_RELOAD",
        default=True,
    )
    workers: int = Field(
        alias="APP_WORKERS",
        default=4,
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


class RabbitMQSettings(BaseSettings):
    user: str = Field(
        alias="RABBITMQ_USER",
        default="guest",
    )
    password: str = Field(
        alias="RABBITMQ_PASSWORD",
        default="guest",
    )
    host: str = Field(
        alias="RABBITMQ_HOST",
        default="rabbitmq",
    )
    port: int = Field(
        alias="RABBITMQ_PORT",
        default=5672,
    )
    vhost: str = Field(
        alias="RABBITMQ_VHOST",
        default="/",
    )
    mq_product_exchange: str = Field(
        alias="MQ_PRODUCT_EXCHANGE",
        default="Product",
    )
    mq_product_routing_key: str = Field(
        alias="MQ_PRODUCT_ROUTING_KEY",
        default="Product",
    )

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=ENV_FILE,
    )

    @property
    def rabbitmq_url(self):
        return (
            f"amqp://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.vhost}"
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
    file_log_format: str = Field(
        alias="LOGURU_FILE_LOG_FORMAT",
        default=FILE_LOG_FORMAT,
    )
    products_log_name: str = Field(
        alias="LOGURU_PRODUCTS_LOG_NAME",
        default="products.log",
    )
    categories_log_name: str = Field(
        alias="LOGURU_CATEGORIES_LOG_NAME",
        default="categories.log",
    )
    requests_log_name: str = Field(
        alias="LOGURU_REQUESTS_LOG_NAME",
        default="requests.log",
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
        rabbitmq: RabbitMQSettings,
        loguru: LoguruSettings,
    ):
        self.app = app
        self.postgres = postgres
        self.rabbitmq = rabbitmq
        self.loguru = loguru


settings = Settings(
    app=AppSettings(),
    postgres=PostgresSettings(),
    rabbitmq=RabbitMQSettings(),
    loguru=LoguruSettings(),
)
