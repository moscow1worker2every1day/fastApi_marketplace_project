import pytest
import httpx
from tests.unit.fake_users import UserFactory
from tests.helpers import (
    BASE_URL,
    HTTP_CLIENT_TIMEOUT,
    _get_auth_headers,
    _sign_up_user,
)


@pytest.fixture(scope="session")
def fake_user():
    return UserFactory()


@pytest.fixture(scope="function")
async def client():
    """HTTP клиент для тестов."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=HTTP_CLIENT_TIMEOUT) as c:
        yield c


@pytest.fixture(scope="function")
async def headers(client: httpx.AsyncClient) -> dict[str, str]:
    """
    Register admin-user via /auth/sign_up,
    sign in via /auth/sign_in and return Authorization headers.
    """
    user, password = await _sign_up_user(client, role_name="admin")
    return await _get_auth_headers(client, user["email"], password)
