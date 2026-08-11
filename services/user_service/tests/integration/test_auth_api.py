"""Tests for /auth endpoints."""

import uuid

import pytest
import httpx
from tests.helpers import (
    _assert_status_200,
    _assert_status_201,
    _assert_status_401,
    _assert_status_404,
    _assert_status_409,
    _assert_status_422,
    _assert_user_structure,
    _assert_token_structure,
    _create_unique_user_data,
    _get_auth_headers,
    _sign_up_user,
)


class TestAuthAPI:
    """Tests for /auth endpoints."""

    @pytest.mark.asyncio
    async def test_sign_up_success(self, client: httpx.AsyncClient):
        user_data = _create_unique_user_data("user")
        response = await client.post("/auth/sign_up", json=user_data)

        _assert_status_201(response)
        user = response.json()
        _assert_user_structure(user)
        assert user["email"] == user_data["email"]
        assert user["first_name"] == user_data["first_name"]
        assert user["last_name"] == user_data["last_name"]
        assert user["role"] == "user"
        assert user["active"] is True

    @pytest.mark.asyncio
    async def test_sign_up_duplicate_email(self, client: httpx.AsyncClient):
        user, _ = await _sign_up_user(client)
        duplicate = _create_unique_user_data("user")
        duplicate["email"] = user["email"]

        response = await client.post("/auth/sign_up", json=duplicate)

        _assert_status_409(response)
        assert "already exist" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_sign_up_invalid_payload(self, client: httpx.AsyncClient):
        response = await client.post(
            "/auth/sign_up",
            json={"email": "not-an-email", "password": "x"},
        )
        _assert_status_422(response)

    @pytest.mark.asyncio
    async def test_sign_in_success(self, client: httpx.AsyncClient):
        user, password = await _sign_up_user(client)

        response = await client.post(
            "/auth/sign_in",
            data={"username": user["email"], "password": password},
        )

        _assert_status_200(response)
        _assert_token_structure(response.json(), expect_refresh=True)

    @pytest.mark.asyncio
    async def test_sign_in_wrong_password(self, client: httpx.AsyncClient):
        user, _ = await _sign_up_user(client)

        response = await client.post(
            "/auth/sign_in",
            data={"username": user["email"], "password": "wrong-password"},
        )

        _assert_status_401(response)

    @pytest.mark.asyncio
    async def test_sign_in_unknown_email(self, client: httpx.AsyncClient):
        response = await client.post(
            "/auth/sign_in",
            data={
                "username": f"missing_{uuid.uuid4().hex[:8]}@example.com",
                "password": "password",
            },
        )
        _assert_status_404(response)

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: httpx.AsyncClient):
        user, password = await _sign_up_user(client)
        sign_in = await client.post(
            "/auth/sign_in",
            data={"username": user["email"], "password": password},
        )
        _assert_status_200(sign_in)
        refresh_token = sign_in.json()["refresh_token"]

        response = await client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        _assert_status_200(response)
        data = response.json()
        assert isinstance(data["access_token"], str)
        assert data["access_token"] != refresh_token

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, client: httpx.AsyncClient):
        user, password = await _sign_up_user(client)
        headers = await _get_auth_headers(client, user["email"], password)

        response = await client.post("/auth/refresh", headers=headers)

        _assert_status_401(response)