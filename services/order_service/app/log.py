from loguru import logger

import os

from loguru import logger

from app.config import settings
from app.constants import SLOW_REQUEST_THRESHOLD_SEC


def _patch_record(record):
    """Ensure format keys always exist outside request context."""
    record["extra"].setdefault("processing_time", 0)


def configure_logging():
    logger.remove()
    logger.configure(patcher=_patch_record)

    os.makedirs(settings.loguru.logs_dir, exist_ok=True)

    common = dict(
        rotation=settings.loguru.rotation,
        retention=settings.loguru.retention,
        encoding=settings.loguru.encoding,
        format=settings.loguru.log_format,
    )

    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.order_log_name),
        level=settings.loguru.log_level,
        filter=lambda record: record["extra"].get("route_group") == "order",
        **common,
    )
    logger.add(
        os.path.join(settings.loguru.logs_dir, settings.loguru.slow_requests_log_name),
        level="INFO",
        filter=lambda record: (
            record["extra"].get("route_group") == "requests"
            and record["extra"].get("processing_time", 0) > SLOW_REQUEST_THRESHOLD_SEC
        ),
        **common,
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


configure_logging()

startup_logger = logger.bind(route_group="startup")
order_logger = logger.bind(route_group="order")
request_logger = logger.bind(route_group="requests")
