import traceback

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.constants import CUSTOM_ERROR_MESSAGES
from app.log import request_logger


async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Handles unhandled exceptions.
    Returns a structured JSON 500 without leaking internal details.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error = CUSTOM_ERROR_MESSAGES.get(status_code, "Internal server error")
    request_logger.error(
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
