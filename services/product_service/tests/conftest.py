import pytest
import httpx
from tests.helpers import (
    BASE_URL,
    HTTP_CLIENT_TIMEOUT,
    _get_auth_headers,
    _sign_up_user,
)

@pytest.fixture
async def user_client():
    async with httpx.AsyncClient(base_url=USER_SERVICE_URL, timeout=15) as c:
        yield c
@pytest.fixture
async def product_client():
    async with httpx.AsyncClient(base_url=PRODUCT_SERVICE_URL, timeout=15) as c:
        yield c