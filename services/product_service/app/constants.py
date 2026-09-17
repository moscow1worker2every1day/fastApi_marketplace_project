"""Constants for the application."""

# Default env file for Pydantic Settings (override with APP_ENV_FILE).
DEFAULT_ENV_FILE = ".env"

# Slow request threshold in seconds (the same log goes into requests and slow_requests).
SLOW_REQUEST_THRESHOLD_SEC = 1.0

# Redis cache key prefix for product read endpoints
PRODUCT_CACHE_PREFIX = "product"
PRODUCTS_CACHE_PREFIX = "products"
CATEGORY_CACHE_PREFIX = "category"
CATEGORIES_CACHE_PREFIX = "categories"

# OpenAPI examples (description, examples, etc.)
EXAMPLE_UUID = "550e8400-e29b-41d4-a716-446655440001"

OPENAPI_DESCRIPTION = (
    "REST API for products and categories management in the marketplace.\n\n"
    "### Products\n"
    "Create, list, fetch, and delete products. "
    "Product creation requires a valid `category_id` and `seller_id` query parameters.\n\n"
    "### Categories\n"
    "Manage the product catalog hierarchy: create root and nested categories, "
    "update descriptions, and delete categories.\n\n"
    "### Integration\n"
    "Seller validation is performed via RabbitMQ request to User Service."
)

OPENAPI_TAGS = [
    {
        "name": "Products",
        "description": "Product CRUD and availability management.",
    },
    {
        "name": "Categories",
        "description": "Category CRUD and hierarchy management.",
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
