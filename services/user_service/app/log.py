"""Конфигурация логирования Loguru для приложения."""

import os

from loguru import logger
from app.config import settings


def configure_logging():
    """Configure logging for the application."""

    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.auth_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "auth",
        rotation=settings.loguru.rotation,
        retention=settings.loguru.retention,
        encoding=settings.loguru.encoding,
        format=settings.loguru.log_format,
    )
    logger.add(

    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.requests_log_name),
        rotation=settings.loguru.rotation,
        retention=settings.loguru.retention,
        encoding=settings.loguru.encoding,
        format=settings.loguru.log_format,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, "slow_requests.log"),
        level="INFO",
        filter=lambda record: (
            record["extra"].get("route_group") == settings.loguru.request_log_name
            and record["extra"].get("extra", {}).get("processing_time", 0) > 1.0
        ),
        rotation=settings.loguru.rotation,
        retention=settings.loguru.retention,
        encoding=settings.loguru.encoding,
        format=settings.loguru.file_log_format,
    )

startup_logger = logger.bind(route_group=settings.loguru.startup_log_name)
auth_logger = logger.bind(router_group=settings.loguru.auth_log_name)
users_logger = logger.bind(router_group=settings.loguru.users_log_name)
request_logger = logger.bind(router_group=settings.loguru.requests_log_name)
slow_requests_logger = logger.bind(router_group=settings.loguru.slow_requests_log_name)
errors_logger = logger.bind(router_group=settings.loguru.errors_log_name)
