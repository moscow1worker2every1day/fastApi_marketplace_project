"""Constants for the application."""


# Slow request threshold in seconds (the same log goes into requests and slow_requests).
SLOW_REQUEST_THRESHOLD_SEC = 1.0

# Default environment file
DEFAULT_ENV_FILE = ".env"

# OpenAPI description
OPENAPI_DESCRIPTION = (
    "REST API for users authorization with JWT authentication "
    "and management with RBAC."
)

# OpenAPI tags
OPENAPI_TAGS = [
    {
        "name": "Authorization",
        "description": "Sign up, sign in and token refresh.",
    },
    {
        "name": "User Account",
        "description": "Current authenticated user profile.",
    },
    {
        "name": "CRUD",
        "description": "User management (get, list, update, delete).",
    },
    {
        "name": "Technical",
        "description": "Health and service diagnostics.",
    },
]

# Format for request logging
REQUEST_LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> -- "
        "<level>{level}</level> -- "
        "<white>{message}</white>"
    )

# Simple format for file logging
FILE_LOG_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} -- "
        "{level} -- "
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
