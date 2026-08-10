import os
import uuid
import httpx
from dotenv import load_dotenv

# Загружаем переменные окружения из файлов .env и .env.test
_project_root = os.path.join(os.path.dirname(__file__), "..")
load_dotenv(os.path.join(_project_root, ".env"))
load_dotenv(os.path.join(_project_root, ".env.test"), override=True)

APP_PORT = os.getenv("TEST_APP_PORT", "39030")
APP_HOST = os.getenv("TEST_APP_HOST", "localhost")
BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
HTTP_CLIENT_TIMEOUT = int(os.getenv("HTTP_CLIENT_TIMEOUT", "10"))


async def _get_auth_headers(client: httpx.AsyncClient, email: str, password: str) -> dict[str, str]:
    """Получает заголовки авторизации для указанного пользователя."""
    response = await client.post("/auth/sign_in", json={"email": email, "password": password})
    assert response.status_code == 200, f"Failed to sign in as {email}: {response.text}"
    data = response.json()
    token = data["access"]
    return {"Authorization": f"Bearer {token}"}


def _assert_status_200(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 200."""
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}. {message}. Response: {response.text}"


def _assert_status_400(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 400."""
    assert response.status_code == 400, \
        f"Expected 400, got {response.status_code}. {message}. Response: {response.text}"


def _assert_status_401(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 401."""
    assert response.status_code == 401, \
        f"Expected 401, got {response.status_code}. {message}. Response: {response.text}"

def _assert_status_404(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 404."""
    assert response.status_code == 404, \
        f"Expected 404, got {response.status_code}. {message}. Response: {response.text}"


def _assert_status_409(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 409."""
    assert response.status_code == 409, \
        f"Expected 409, got {response.status_code}. {message}. Response: {response.text}"


def _assert_status_403(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 403."""
    assert response.status_code == 403, \
        f"Expected 403, got {response.status_code}. {message}. Response: {response.text}"


def _assert_status_422(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 422 (validation error)."""
    assert response.status_code == 422, \
        f"Expected 422, got {response.status_code}. {message}. Response: {response.text}"


def _assert_user_structure(user: dict[str, any]) -> None:
    expected_keys = {
        "id",
        "first_name",
        "last_name",
        "email",
        "role",
        "created_at",
        "updated_at",
        "hashed_password", 
        "active"
    }
    assert user.keys() == expected_keys, f"User structure is not correct. Got keys: {user.keys()}. Expected keys: {expected_keys}"
    assert isinstance(user["id"], int)
    assert isinstance(user["first_name"], str)
    assert isinstance(user["last_name"], str)
    assert isinstance(user["email"], str)
    assert isinstance(user["role"], str)
    assert isinstance(user["created_at"], str)
    assert isinstance(user["updated_at"], str)
    assert isinstance(user["hashed_password"], str)
    assert isinstance(user["active"], bool)


def _create_unique_user_data(role_name: str) -> dict[str, any]:
    """Create data for a unique user."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test_user_{uuid.uuid4().hex[:8]}@example.com",
        "role": role_name,
        "password": "password"
    }

async def _create_test_user(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    role_name: str,
    **overrides: dict[str, any]
) -> dict[str, str]:
    """Create a test user and return its data."""
    user_data = _create_unique_user_data(role_name)
    user_data.update(overrides)

    response = await client.post("/user", json=user_data, headers=headers)
    _assert_status_200(response, f"Failed to create user: {user_data.get('login', 'unknown')}")
    _assert_user_structure(response.json())
    return response.json()
