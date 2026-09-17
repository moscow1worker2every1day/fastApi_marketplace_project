"""Constants for order_service."""

# Default env file for Pydantic Settings (override with APP_ENV_FILE).
DEFAULT_ENV_FILE = ".env"

# Format for request logging
REQUEST_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> -- "
    "<level>{level}</level> -- "
    "<white>{message}</white>"
)
