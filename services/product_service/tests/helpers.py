import os
from dotenv import load_dotenv

_project_root = os.path.join(os.path.dirname(__file__), "..")
load_dotenv(os.path.join(_project_root, ".env"))
load_dotenv(os.path.join(_project_root, ".env.test"), override=True)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
HTTP_CLIENT_TIMEOUT = int(os.getenv("HTTP_CLIENT_TIMEOUT", "10"))
