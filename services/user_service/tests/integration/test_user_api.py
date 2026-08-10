import asyncio

import pytest
import httpx
from tests.helpers import (
    _assert_status_200,
    _assert_status_401,
    _assert_user_structure,
    _create_test_user
)

class TestUserAPI:
    """Tests for user API endpoints."""

    @pytest.mark.asyncio
    async def test_get_all_users(
        self,
        headers: dict[str, str],
        client: httpx.AsyncClient
    ):
        """Check that /user returns all users."""
        response = await client.get("/user", headers=headers)
        _assert_status_200(response)
        for user in response.json():
            _assert_user_structure(user)

    @pytest.mark.asyncio
    async def test_user_names_list_requires_bearer_token(
        self,
        client: httpx.AsyncClient
    ):
        """Check that /user requires Bearer token."""
        response = await client.get("/user")
        _assert_status_401(response)