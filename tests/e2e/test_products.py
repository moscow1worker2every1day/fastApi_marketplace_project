"""E2E: product create, list filters, soft/hard delete."""

from __future__ import annotations

import pytest

from tests.e2e.helpers import (
    assert_product_structure,
    assert_status,
    create_category,
    create_product,
    sign_up,
    unique_name,
)


class TestProducts:
    """
    Tests for product management:
    - create and get product
    - list products with filters
    - soft/hard delete product
    - create product rejects admin and missing seller
    - create product rejects unknown category
    - category CRUD
    """

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_create_and_get_product(self, user_client, product_client):
        seller, _ = await sign_up(user_client, role="seller")
        category = await create_category(product_client)
        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            name=unique_name("Phone"),
            price=99.5,
            stock=7,
            description="e2e phone",
        )

        got = await product_client.get(f"/products/{product['id']}")
        assert_status(got, 200)
        assert_product_structure(
            got.json(),
            expected_name="Phone",
            expected_price=99.5,
            expected_stock=7,
            expected_description="e2e phone",
            expected_category_id=category["id"],
            expected_seller_id=seller["id"],
        )


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_list_products_only_available_filter(self, user_client, product_client):
        seller, _ = await sign_up(user_client, role="seller")
        category = await create_category(product_client)
        live = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            name=unique_name("Live"),
        )
        soft = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            name=unique_name("SoftGone"),
        )

        soft_delete = await product_client.delete(f"/products/{soft['id']}?mode=soft")
        assert_status(soft_delete, 200)
        assert_product_structure(soft_delete.json(), expected_available=False)

        available_only = await product_client.get(
            "/products/",
            params={"only_available": True, "category_id": category["id"]},
        )
        assert_status(available_only, 200)
        available_ids = {p["id"] for p in available_only.json()}
        assert live["id"] in available_ids
        assert soft["id"] not in available_ids

        # Soft-deleted product remains readable by id
        still_there = await product_client.get(f"/products/{soft['id']}")
        assert_status(still_there, 200)
        assert_product_structure(still_there.json(), expected_available=False)


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_soft_delete_keeps_row_hard_delete_removes(self, user_client, product_client):
        seller, _ = await sign_up(user_client, role="seller")
        category = await create_category(product_client)
        soft_target = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
        )
        hard_target = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
        )

        soft = await product_client.delete(f"/products/{soft_target['id']}")  # default soft
        assert_status(soft, 200)
        assert_product_structure(soft.json(), expected_available=False)
        assert_status(await product_client.get(f"/products/{soft_target['id']}"), 200)

        hard = await product_client.delete(f"/products/{hard_target['id']}?mode=delete")
        assert_status(hard, 200)
        assert_status(await product_client.get(f"/products/{hard_target['id']}"), 404)


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_create_product_rejects_admin_and_missing_seller(self, user_client, product_client):
        admin, _ = await sign_up(user_client, role="admin")
        category = await create_category(product_client)

        as_admin = await product_client.post(
            f"/products/?seller_id={admin['id']}&category_id={category['id']}",
            json={"name": unique_name("AdminItem"), "price": 5.0, "stock": 1},
        )
        assert_status(as_admin, 403, "admin is not a seller for product create")

        missing = await product_client.post(
            f"/products/?seller_id=00000000-0000-0000-0000-000000000099&category_id={category['id']}",
            json={"name": unique_name("Ghost"), "price": 5.0, "stock": 1},
        )
        assert_status(missing, 404, "unknown seller_id must be 404")


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_create_product_rejects_unknown_category(self, user_client, product_client):
        seller, _ = await sign_up(user_client, role="seller")
        response = await product_client.post(
            f"/products/?seller_id={seller['id']}&category_id=00000000-0000-0000-0000-000000000088",
            json={"name": unique_name("NoCat"), "price": 3.0, "stock": 1},
        )
        assert_status(response, 404)
