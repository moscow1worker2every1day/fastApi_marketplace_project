"""Tests for /users endpoints."""
import uuid

import pytest
import httpx
from tests.helpers import (
    _assert_status_200,
    _assert_status_401,
    _assert_status_403,
    _assert_status_404,
    _assert_status_409,
    _assert_status_422,
    _assert_user_structure,
    _get_auth_headers,
    _sign_up_user,
)


def _assert_token_structure(data: dict, *, expect_refresh: bool = True) -> None:
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data.get("token_type", "Bearer") == "Bearer"
    if expect_refresh:
        assert "refresh_token" in data
        assert isinstance(data["refresh_token"], str)


class TestUserAPI:
    """Tests for /users endpoints."""

    @pytest.mark.asyncio
    async def test_get_all_users(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        """Check that /users returns a paginated page for admin."""
        await _sign_up_user(client)
        response = await client.get("/users/", headers=headers)

        _assert_status_200(response)
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1
        for user in users:
            _assert_user_structure(user)

    @pytest.mark.asyncio
    async def test_get_all_users_with_limit_offset(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        await _sign_up_user(client)
        await _sign_up_user(client)

        response = await client.get(
            "/users/",
            params={"limit": 1, "offset": 0},
            headers=headers,
        )

        _assert_status_200(response)
        body = response.json()
        assert isinstance(body, list)
        assert len(body) == 1
        _assert_user_structure(body[0])

    @pytest.mark.asyncio
    async def test_get_all_users_sort_by_first_name(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        await _sign_up_user(client, first_name="Charlie")
        await _sign_up_user(client, first_name="Alice")
        await _sign_up_user(client, first_name="Bob")

        response = await client.get(
            "/users/",
            params={"sort_by": "first_name", "sort_order": "asc"},
            headers=headers,
        )

        _assert_status_200(response)
        first_names = [user["first_name"] for user in response.json()]
        assert first_names == sorted(first_names)

        response = await client.get(
            "/users/",
            params={"sort_by": "first_name", "sort_order": "desc"},
            headers=headers,
        )

        _assert_status_200(response)
        first_names = [user["first_name"] for user in response.json()]
        assert first_names == sorted(first_names, reverse=True)

    @pytest.mark.asyncio
    async def test_get_all_users_invalid_sort_field(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        response = await client.get(
            "/users/",
            params={"sort_by": "invalid_field"},
            headers=headers,
        )

        _assert_status_422(response)

    @pytest.mark.asyncio
    async def test_get_all_users_forbidden_for_regular_user(
        self,
        client: httpx.AsyncClient,
    ):
        user, password = await _sign_up_user(client, role_name="user")
        user_headers = await _get_auth_headers(client, user["email"], password)

        response = await client.get("/users/", headers=user_headers)

        _assert_status_403(response)

    @pytest.mark.asyncio
    async def test_get_all_users_unauthorized(self, client: httpx.AsyncClient):
        response = await client.get("/users/")
        _assert_status_401(response)

    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        """Check that /users/{user_id} returns user by id."""
        user, _ = await _sign_up_user(client)
        response = await client.get(f"/users/{user['id']}", headers=headers)

        _assert_status_200(response)
        body = response.json()
        _assert_user_structure(body)
        assert body["id"] == user["id"]
        assert body["email"] == user["email"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        missing_id = uuid.uuid4()
        response = await client.get(f"/users/{missing_id}", headers=headers)

        _assert_status_404(response)
        assert str(missing_id) in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_my_account(
        self,
        client: httpx.AsyncClient,
    ):
        user, password = await _sign_up_user(client)
        user_headers = await _get_auth_headers(client, user["email"], password)

        response = await client.get("/users/account/my_account/", headers=user_headers)

        _assert_status_200(response)
        body = response.json()
        _assert_user_structure(body)
        assert body["id"] == user["id"]
        assert body["email"] == user["email"]

    @pytest.mark.asyncio
    async def test_update_user_name(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        user, _ = await _sign_up_user(client)
        payload = {
            "id": user["id"],
            "first_name": "Updated",
            "last_name": "Name",
        }

        response = await client.put(
            f"/users/{user['id']}/name",
            json=payload,
            headers=headers,
        )

        _assert_status_200(response)
        body = response.json()
        _assert_user_structure(body)
        assert body["first_name"] == "Updated"
        assert body["last_name"] == "Name"
        assert body["id"] == user["id"]

    @pytest.mark.asyncio
    async def test_update_user_name_not_found(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        missing_id = uuid.uuid4()
        response = await client.put(
            f"/users/{missing_id}/name",
            json={"id": str(missing_id), "first_name": "Ghost"},
            headers=headers,
        )
        _assert_status_404(response)

    @pytest.mark.asyncio
    async def test_update_user_email(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        user, _ = await _sign_up_user(client)
        new_email = f"updated_{uuid.uuid4().hex[:8]}@example.com"
        payload = {"id": user["id"], "email": new_email}

        response = await client.put(
            f"/users/{user['id']}/email",
            json=payload,
            headers=headers,
        )

        _assert_status_200(response)
        body = response.json()
        _assert_user_structure(body)
        assert body["email"] == new_email
        assert body["id"] == user["id"]

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        first, _ = await _sign_up_user(client)
        second, _ = await _sign_up_user(client)

        response = await client.put(
            f"/users/{second['id']}/email",
            json={"id": second["id"], "email": first["email"]},
            headers=headers,
        )

        _assert_status_409(response)

    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        user, _ = await _sign_up_user(client)

        response = await client.delete(f"/users/{user['id']}", headers=headers)

        _assert_status_200(response)
        body = response.json()
        assert body["user_id"] == user["id"]
        assert body["message"] == f"User with id={user['id']} deleted successfully: True"

        get_response = await client.get(f"/users/{user['id']}", headers=headers)
        _assert_status_404(get_response)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient,
    ):
        missing_id = uuid.uuid4()
        response = await client.delete(f"/users/{missing_id}", headers=headers)
        _assert_status_404(response)
