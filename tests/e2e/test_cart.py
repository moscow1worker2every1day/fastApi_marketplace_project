"""E2E: cart management and product-event side effects."""

from __future__ import annotations
import asyncio

import pytest

from tests.e2e.helpers import (
    add_to_cart,
    assert_cart_structure,
    assert_status,
    create_category,
    create_product,
    sign_up,
)


class TestCart:
    """
    Tests for cart management and product-event side effects:
    - cart add, change, remove, clear
    - cart decrease to zero removes line
    - hard delete product removes from cart
    - soft delete product removes from cart
    - carts are isolated per user
    """

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_cart_modification(self, user_client, product_client, cart_client):
        seller, _ = await sign_up(user_client, role="seller")
        buyer, _ = await sign_up(user_client, role="user")
        category = await create_category(product_client)
        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            price=20.0,
            stock=10,
        )

        empty = await cart_client.get(f"/cart/{buyer['id']}")
        assert_status(empty, 200)
        assert_cart_structure(empty.json())

        added = await add_to_cart(
            cart_client,
            user_id=buyer["id"],
            product_id=product["id"],
            quantity=1,
            price=20.0,
        )
        assert_status(added, 200, "add to cart failed")
        cart = added.json()
        assert_cart_structure(cart, expected_items=[product["id"]], expected_total=20.0)

        increased = await cart_client.put(
            f"/cart/{buyer['id']}/change/{product['id']}",
            params={"delta": 1},
        )
        assert_status(increased, 200, "increase quantity failed")
        cart = increased.json()
        assert_cart_structure(cart, expected_items=[product["id"]], expected_total=40.0)

        decreased = await cart_client.put(
            f"/cart/{buyer['id']}/change/{product['id']}",
            params={"delta": -1},
        )
        assert_status(decreased, 200, "decrease quantity failed")
        cart = decreased.json()
        assert_cart_structure(cart, expected_items=[product["id"]], expected_total=20.0)

        removed = await cart_client.delete(
            f"/cart/{buyer['id']}/remove/{product['id']}",
        )
        assert_status(removed, 200, "remove from cart failed")
        cart = removed.json()
        assert_cart_structure(cart)

        # re-add then clear
        await add_to_cart(
            cart_client,
            user_id=buyer["id"],
            product_id=product["id"],
            quantity=3,
            price=20.0,
        )
        cleared = await cart_client.delete(f"/cart/{buyer['id']}/clear")
        assert_status(cleared, 200, "clear cart failed")
        cart = cleared.json()
        assert_cart_structure(cart)


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_cart_decrease_to_zero_removes_line(self, user_client, product_client, cart_client):
        seller, _ = await sign_up(user_client, role="seller")
        buyer, _ = await sign_up(user_client, role="user")
        category = await create_category(product_client)
        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            price=8.0,
        )
        await add_to_cart(
            cart_client,
            user_id=buyer["id"],
            product_id=product["id"],
            quantity=1,
            price=8.0,
        )

        response = await cart_client.put(
            f"/cart/{buyer['id']}/change/{product['id']}",
            params={"delta": -1},
        )
        assert_status(response, 200, "decrease quantity failed")
        cart = response.json()
        assert_cart_structure(cart)


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_hard_delete_product_removes_from_cart(self, 
        user_client,
        product_client,
        cart_client,
    ):
        seller, _ = await sign_up(user_client, role="seller")
        buyer, _ = await sign_up(user_client, role="user")
        category = await create_category(product_client)
        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            price=12.5,
        )
        await add_to_cart(
            cart_client,
            user_id=buyer["id"],
            product_id=product["id"],
            quantity=1,
            price=12.5,
        )

        deleted = await product_client.delete(f"/products/{product['id']}?mode=delete")
        assert_status(deleted, 200, "hard delete product failed")
        await asyncio.sleep(1) # wait for product event to be processed

        response = await cart_client.get(f"/cart/{buyer['id']}")
        assert_status(response, 200, "get cart failed")
        assert_cart_structure(response.json())


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_soft_delete_product_removes_from_cart(self, 
        user_client,
        product_client,
        cart_client,
    ):
        seller, _ = await sign_up(user_client, role="seller")
        buyer, _ = await sign_up(user_client, role="user")
        category = await create_category(product_client)
        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            price=15.0,
        )
        await add_to_cart(
            cart_client,
            user_id=buyer["id"],
            product_id=product["id"],
            quantity=2,
            price=15.0,
        )

        soft = await product_client.delete(f"/products/{product['id']}?mode=soft")
        assert_status(soft, 200, "soft delete product failed")
        assert soft.json()["available"] is False

        await asyncio.sleep(1) # wait for product event to be processed
        response = await cart_client.get(f"/cart/{buyer['id']}")
        assert_status(response, 200, "get cart failed")
        assert_cart_structure(response.json())

        # product still exists in catalog as unavailable
        got = await product_client.get(f"/products/{product['id']}")
        assert_status(got, 200)
        assert got.json()["available"] is False


    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_user_cart_is_forbidden_per_user(self, user_client, product_client, cart_client):
        seller, _ = await sign_up(user_client, role="seller")
        buyer, _ = await sign_up(user_client, role="user")
        other_buyer, _ = await sign_up(user_client, role="user")
        category = await create_category(product_client)
        product = await create_product(
            product_client,
            seller_id=seller["id"],
            category_id=category["id"],
            price=9.0,
        )

        await add_to_cart(
            cart_client,
            user_id=buyer["id"],
            product_id=product["id"],
            quantity=1,
            price=9.0,
        )

        response = await cart_client.get(f"/cart/{buyer['id']}")
        assert_status(response, 200, "get cart b failed")
        assert_cart_structure(response.json())

        response = await cart_client.get(f"/cart/{other_buyer['id']}")
        assert_status(response, 403, "get cart a failed")
