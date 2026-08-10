"""Constants for the application."""

DEFAULT_ENV_FILE = ".env"

OPENAPI_TAGS = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "auth",
        "description": "Operations with authentication.",
    },
]

# Format for request logging
REQUEST_LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> -- "
        "<level>{level}</level> -- "
        "<cyan>{extra[request_id]}</cyan> -- "
        "<white>{message}</white>"
    )

# Simple format for file logging
FILE_LOG_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} -- "
        "{level} -- "
        "{extra[request_id]} -- "
        "{message}"
    )

CUSTOM_ERROR_MESSAGES = {
    400: "Bad request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Resource not found",
    409: "Data conflict",
    422: "Request validation error",
    500: "Internal server error",
    502: "Bad gateway",
    503: "Service unavailable",
    504: "Server timeout",
}
