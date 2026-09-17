"""E2E config: URLs and timeouts for black-box tests against a running stack."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Prefer dedicated e2e env; fall back to root .env / process env.
load_dotenv(_REPO_ROOT / ".env")
load_dotenv(_REPO_ROOT / ".env.e2e", override=True)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000").rstrip("/")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001").rstrip("/")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://localhost:8002").rstrip("/")
# ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003").rstrip("/")

HTTP_CLIENT_TIMEOUT = float(os.getenv("HTTP_CLIENT_TIMEOUT", "15"))
HEALTH_TIMEOUT_SEC = float(os.getenv("E2E_HEALTH_TIMEOUT_SEC", "120"))
HEALTH_POLL_INTERVAL_SEC = float(os.getenv("E2E_HEALTH_POLL_INTERVAL_SEC", "2"))
EVENTUAL_TIMEOUT_SEC = float(os.getenv("E2E_EVENTUAL_TIMEOUT_SEC", "15"))
EVENTUAL_POLL_INTERVAL_SEC = float(os.getenv("E2E_EVENTUAL_POLL_INTERVAL_SEC", "0.5"))

SERVICE_URLS = {
    "user": USER_SERVICE_URL,
    "product": PRODUCT_SERVICE_URL,
    "cart": CART_SERVICE_URL,
}
