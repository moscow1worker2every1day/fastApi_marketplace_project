"""E2E: product_service ↔ user_service via RabbitMQ RPC (seller check)."""

from __future__ import annotations

import pytest

from tests.e2e.helpers import assert_status, create_category, create_product, sign_up, unique_name


class TestProductSellerCheck:
    """
    Tests for product creation requires seller role (/products/ create):
    - seller can create product
    - non-seller cannot create product
    """

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_create_product_requires_seller_role(self, user_client, product_client):
        seller, _ = await sign_up(user_client, role="seller")
        regular_user, _ = await sign_up(user_client, role="user")
        category = await create_category(product_client)

        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            name=unique_name("RPC-Seller"),
            price=19.99,
            stock=3,
        )
        assert product["name"].startswith("RPC-Seller")
        assert product["available"] is True

        forbidden = await product_client.post(
            f"/products/?seller_id={regular_user['id']}&category_id={category['id']}",
            json={"name": unique_name("Fail"), "price": 1.0, "stock": 1},
        )
        assert_status(forbidden, 403, "non-seller must be rejected by RPC check")
