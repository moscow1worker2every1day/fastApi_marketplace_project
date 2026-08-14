"""Конфигурация логирования Loguru для приложения."""

import os

from loguru import logger

from app.config import settings
from app.constants import SLOW_REQUEST_THRESHOLD_SEC


def _patch_record(record):
    """Ensure format keys always exist outside request context."""
    record["extra"].setdefault("processing_time", 0)


def configure_logging():
    """Configure logging for the application.

    Distribution by files (one call can fall into several sinks):
    - products.log        — route_group=products
    - categories.log      — route_group=categories
    - requests.log        — all requests (route_group=requests)
    - slow_requests.log   — route_group=requests and processing_time > threshold
    - startup.log         — route_group=startup
    - errors.log          — any ERROR/CRITICAL (without filter by route_group)
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
        os.path.join(settings.loguru.logs_dir, settings.loguru.products_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "products",
        **common,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.categories_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "categories",
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
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.errors_log_name),
        level="ERROR",
        **common,
    )


startup_logger = logger.bind(route_group="startup")
products_logger = logger.bind(route_group="products")
categories_logger = logger.bind(route_group="categories")
request_logger = logger.bind(route_group="requests")
