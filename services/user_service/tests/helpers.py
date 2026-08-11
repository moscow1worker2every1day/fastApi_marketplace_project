import os
import uuid
import httpx
from dotenv import load_dotenv

# Загружаем переменные окружения из файлов .env и .env.test
_project_root = os.path.join(os.path.dirname(__file__), "..")
load_dotenv(os.path.join(_project_root, ".env"))
load_dotenv(os.path.join(_project_root, ".env.test"), override=True)

APP_PORT = os.getenv("TEST_APP_PORT", "8000")
APP_HOST = os.getenv("TEST_APP_HOST", "localhost")
APP_VERSION = os.getenv("DEPLOY_VERSION", "unknown")
BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
HTTP_CLIENT_TIMEOUT = int(os.getenv("HTTP_CLIENT_TIMEOUT", "10"))

OPENAPI_PATHS = {
    "/healthcheck",
    "/auth/sign_up",
    "/auth/sign_in",
    "/auth/refresh",
    "/users/",
    "/users/account/my_account/",
    "/users/{user_id}",
    "/users/{user_id}/name",
    "/users/{user_id}/email",
}

async def _get_auth_headers(
    client: httpx.AsyncClient, email: str, password: str
) -> dict[str, str]:
    """Get authorization headers for a given user via /auth/sign_in."""
    response = await client.post(
        "/auth/sign_in",
        data={"username": email, "password": password},
    )
    _assert_status_200(response, f"Failed to sign in as {email}")
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _assert_status_200(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 200."""
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_201(response: httpx.Response, message: str = "") -> None:
    """Check that status code is 201."""
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_400(response: httpx.Response, message: str = "") -> None:
    assert response.status_code == 400, (
        f"Expected 400, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_401(response: httpx.Response, message: str = "") -> None:
    assert response.status_code == 401, (
        f"Expected 401, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_404(response: httpx.Response, message: str = "") -> None:
    assert response.status_code == 404, (
        f"Expected 404, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_409(response: httpx.Response, message: str = "") -> None:
    assert response.status_code == 409, (
        f"Expected 409, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_403(response: httpx.Response, message: str = "") -> None:
    assert response.status_code == 403, (
        f"Expected 403, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_status_422(response: httpx.Response, message: str = "") -> None:
    assert response.status_code == 422, (
        f"Expected 422, got {response.status_code}. {message}. Response: {response.text}"
    )


def _assert_user_structure(user: dict) -> None:
    expected_keys = {
        "id",
        "first_name",
        "last_name",
        "email",
        "role",
        "created_at",
        "updated_at",
        "active",
    }
    assert user.keys() == expected_keys, (
        f"User structure is not correct. Got keys: {user.keys()}. "
        f"Expected keys: {expected_keys}"
    )
    # UUID сериализуется в JSON как строка
    assert isinstance(user["id"], str)
    assert isinstance(user["first_name"], str)
    assert isinstance(user["last_name"], str)
    assert isinstance(user["email"], str)
    assert isinstance(user["role"], str)
    assert isinstance(user["created_at"], str)
    assert isinstance(user["updated_at"], str)
    assert isinstance(user["active"], bool)


def _assert_token_structure(data: dict, *, expect_refresh: bool = True) -> None:
    expected_keys = {
        "access_token": str,
    }
    if expect_refresh:
        expected_keys["refresh_token"] = str
    assert all(key in data for key in expected_keys.keys()), (
        f"Token structure is not correct. Got keys: {data.keys()}. "
        f"Expected keys: {expected_keys.keys()}"
    )
    assert all(data[key] is not None and isinstance(data[key], expected_keys[key]) for key in expected_keys.keys()), (
        f"Token structure is not correct. Got values: {data.values()}. "
        f"Expected values: {expected_keys.values()}"
    )


def _create_unique_user_data(role_name: str) -> dict:
    """Create data for a unique user."""
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test_user_{uuid.uuid4().hex[:8]}@example.com",
        "role": role_name,
        "password": "password",
    }


async def _sign_up_user(
    client: httpx.AsyncClient,
    role_name: str = "user",
    **overrides,
) -> tuple[dict, str]:
    """
    Register user via /auth/sign_up.
    Returns (user_json, plain_password).
    """
    user_data = _create_unique_user_data(role_name)
    user_data.update(overrides)
    password = user_data["password"]

    response = await client.post("/auth/sign_up", json=user_data)
    _assert_status_201(
        response, f"Failed to sign up user: {user_data.get('email', 'unknown')}"
    )
    user = response.json()
    _assert_user_structure(user)
    return user, password
