import traceback
from fastapi import Request, status, JSONResponse

from app.constants import CUSTOM_ERROR_MESSAGES
from services.user_service.app.log import errors_logger, request_logger


async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Обрабатывает необработанные исключения.
    Возвращает структурированный JSON 500 без утечки внутренних деталей.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error = CUSTOM_ERROR_MESSAGES.get(status_code, "Internal server error")
    errors_logger.error(
        f"Unhandled exception: {type(exc).__name__}: {exc}\n"
        f"{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "error": error,
            "details": "An unexpected error occurred.",
        },
    )

