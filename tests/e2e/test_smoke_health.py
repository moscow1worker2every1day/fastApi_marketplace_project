"""Smoke: all services respond on /healthcheck."""

import pytest

from tests.e2e.helpers import assert_status, create_category, assert_product_structure


class TestSmokeHealth:
    """
    Tests for smoke health:
    - services health
    - category CRUD smoke
    """

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_services_health(self, user_client, product_client, cart_client):
        for client in (user_client, product_client, cart_client):
            response = await client.get("/healthcheck")
            assert_status(response, 200, "healthcheck failed")

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_category_crud_smoke(self, product_client):
        created = await create_category(product_client, description="root cat")
        got = await product_client.get(f"/categories/{created['id']}")
        assert_status(got, 200)
        assert_product_structure(got.json(), expected_name=created["name"])

        updated = await product_client.put(
            f"/categories/{created['id']}/description",
            json={"description": "updated-e2e"},
        )
        assert_status(updated, 200)
        assert_product_structure(updated.json(), expected_description="updated-e2e")