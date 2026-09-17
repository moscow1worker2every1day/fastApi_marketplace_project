"""Constants for the application."""

# Threshold for slow requests
SLOW_REQUEST_THRESHOLD_SEC = 1.0

# Format for request logging
LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> -- "
        "<level>{level}</level> -- "
        "<white>{message}</white>"
    )