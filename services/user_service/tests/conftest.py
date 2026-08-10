import pytest
from tests.unit.fake_users import UserFactory
import httpx
from tests.helpers import BASE_URL, HTTP_CLIENT_TIMEOUT

@pytest.fixture(scope="session")
def fake_user():
    return UserFactory()

@pytest.fixture(scope="function")
async def client():
    """HTTP клиент для тестов."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=HTTP_CLIENT_TIMEOUT) as c:
        yield c
