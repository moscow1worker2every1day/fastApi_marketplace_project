"""Конфигурация логирования Loguru для приложения."""

import os

from loguru import logger
from app.config import settings
from app.constants import SLOW_REQUEST_THRESHOLD_SEC


def _patch_record(record):
    """Ensure format keys always exist outside request context."""
    record["extra"].setdefault("request_id", "-")
    record["extra"].setdefault("processing_time", 0)


def configure_logging():
    """Configure logging for the application.

    Один вызов logger.info/error может попасть в несколько sinks:
    - requests.log  — все записи с route_group=requests
    - slow_requests — те же записи, если processing_time > порога
    - errors.log    — любые записи уровня ERROR+ (из любого route_group)
    """
    logger.remove()
    logger.configure(patcher=_patch_record)

    common = dict(
        rotation=settings.loguru.rotation,
        retention=settings.loguru.retention,
        encoding=settings.loguru.encoding,
        format=settings.loguru.log_format,
    )

    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.auth_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "auth",
        **common,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.users_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "users",
        **common,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.requests_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "requests",
        **common,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.slow_requests_log_name),
        level="INFO",
        filter=lambda record: (
            record["extra"].get("route_group") == "requests"
            and record["extra"].get("processing_time", 0) > SLOW_REQUEST_THRESHOLD_SEC
        ),
        rotation=settings.loguru.rotation,
        retention=settings.loguru.retention,
        encoding=settings.loguru.encoding,
        format=settings.loguru.file_log_format,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.startup_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "startup",
        **common,
    )
    # Без filter по route_group: все ERROR/CRITICAL из auth/users/startup/requests.
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.errors_log_name),
        level="ERROR",
        **common,
    )


startup_logger = logger.bind(route_group="startup", request_id="-")
auth_logger = logger.bind(route_group="auth", request_id="-")
users_logger = logger.bind(route_group="users", request_id="-")
