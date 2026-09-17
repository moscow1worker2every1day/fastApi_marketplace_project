import json
from uuid import UUID

from app.storage.redis.connection import RedisService


def _cart_key(user_id: UUID) -> str:
    return f"cart:{user_id}"


def _product_key(product_id: UUID) -> str:
    return f"cart:product:{product_id}"


def _parse_cart(cart_data: str | bytes | None) -> dict | None:
    if not cart_data:
        return None
    if isinstance(cart_data, bytes):
        cart_data = cart_data.decode()
    return json.loads(cart_data)


def _recalculate_total(cart: dict) -> float:
    return sum(item["price"] * item["quantity"] for item in cart["items"])


class CartRepository:

    @staticmethod
    async def _get_cart(user_id: UUID) -> dict | None:
        cart = await RedisService.get_connection().get(_cart_key(user_id))
        return _parse_cart(cart)

    @staticmethod
    async def _set_cart(user_id: UUID, cart: dict) -> None:
        await RedisService.get_connection().set(
            _cart_key(user_id),
            json.dumps(cart),
        )

    @staticmethod
    async def _remove_cart(user_id: UUID) -> None:
        await RedisService.get_connection().delete(_cart_key(user_id))
    
    @staticmethod
    async def _remove_product(product_id: UUID) -> None:
        await RedisService.get_connection().delete(_product_key(product_id))

    @staticmethod
    async def _get_users_by_product(product_id: UUID) -> set[UUID]:
        members = await RedisService.get_connection().smembers(
            _product_key(product_id)
        )
        return {UUID(member) for member in members}

    @staticmethod
    async def _set_users_by_product(product_id: UUID, user_id: UUID) -> None:
        await RedisService.get_connection().sadd(
            _product_key(product_id),
            str(user_id),
        )

    @staticmethod
    async def _remove_users_by_product(product_id: UUID, user_id: UUID) -> None:
        await RedisService.get_connection().srem(
            _product_key(product_id),
            str(user_id),
        )

    @staticmethod
    async def get_cart(user_id: UUID) -> dict | None:
        return await CartRepository._get_cart(user_id)

    @staticmethod
    async def change_quantity(
        user_id: UUID,
        product_id: UUID,
        delta: int,
    ) -> dict | None:
        cart = await CartRepository._get_cart(user_id)
        if cart is None:
            return None

        product_id_value = str(product_id)
        updated = False
        for item in list(cart["items"]):
            if item["product_id"] == product_id_value:
                item["quantity"] += delta
                if item["quantity"] <= 0:
                    cart["items"].remove(item)
                    await CartRepository._remove_users_by_product(
                        product_id=product_id,
                        user_id=user_id,
                    )
                updated = True
                break

        if not updated:
            raise ValueError(f"Product {product_id} not found in cart")

        cart["total"] = _recalculate_total(cart)
        if not cart["items"]:
            await CartRepository._remove_cart(user_id)
            return {"items": [], "total": 0.0}

        await CartRepository._set_cart(user_id, cart)
        return cart

    @staticmethod
    async def add_to_cart(
        user_id: UUID,
        product_id: UUID,
        price: float,
        quantity: int = 1,
    ) -> dict:
        cart = await CartRepository._get_cart(user_id)
        product_id_value = str(product_id)

        if cart is None:
            cart = {
                "items": [
                    {
                        "product_id": product_id_value,
                        "price": price,
                        "quantity": quantity,
                    }
                ],
                "total": price * quantity,
            }
        else:
            found = False
            for existing_item in cart["items"]:
                if existing_item["product_id"] == product_id_value:
                    existing_item["quantity"] += quantity
                    cart["total"] += price * quantity
                    found = True
                    break
            if not found:
                cart["items"].append(
                    {
                        "product_id": product_id_value,
                        "price": price,
                        "quantity": quantity,
                    }
                )
                cart["total"] += price * quantity

        await CartRepository._set_cart(user_id, cart)
        await CartRepository._set_users_by_product(product_id, user_id)
        return cart

    @staticmethod
    async def delete_from_cart(user_id: UUID, product_id: UUID) -> dict | None:
        cart = await CartRepository._get_cart(user_id)
        if cart is None:
            return None

        product_id_value = str(product_id)
        cart["items"] = [
            item for item in cart["items"] if item["product_id"] != product_id_value
        ]
        cart["total"] = _recalculate_total(cart) if cart["items"] else 0.0

        await CartRepository._remove_users_by_product(product_id, user_id)
        if not cart["items"]:
            await CartRepository._remove_cart(user_id)
            return {"items": [], "total": 0.0}

        await CartRepository._set_cart(user_id, cart)
        return cart

    @staticmethod
    async def clear_cart(user_id: UUID) -> None:
        cart = await CartRepository._get_cart(user_id)
        if cart:
            for item in cart["items"]:
                await CartRepository._remove_users_by_product(
                    product_id=UUID(item["product_id"]),
                    user_id=user_id,
                )
        await CartRepository._remove_cart(user_id)

    @staticmethod
    async def remove_product_from_all_carts(product_id: UUID) -> int:
        """Remove product from every cart that contains it. Returns affected carts count."""
        user_ids = await CartRepository._get_users_by_product(product_id)
        affected = 0
        for user_id in user_ids:
            result = await CartRepository.delete_from_cart(
                user_id=user_id,
                product_id=product_id,
            )
            if result is not None:
                affected += 1
        await CartRepository._remove_product(product_id)
        return affected

    @staticmethod
    async def update_product_in_all_carts(
        product_id: UUID,
        *,
        price: float | None = None,
        available: bool | None = None,
    ) -> int:
        if available is False:
            return await CartRepository.remove_product_from_all_carts(product_id)

        if price is None:
            return 0

        user_ids = await CartRepository._get_users_by_product(product_id)
        product_id_value = str(product_id)
        affected = 0

        for user_id in user_ids:
            cart = await CartRepository._get_cart(user_id)
            if cart is None:
                await CartRepository._remove_users_by_product(
                    product_id=product_id,
                    user_id=user_id,
                )
                continue

            updated = False
            for item in cart["items"]:
                if item["product_id"] == product_id_value:
                    item["price"] = price
                    updated = True
                    break

            if updated:
                cart["total"] = _recalculate_total(cart)
                await CartRepository._set_cart(user_id, cart)
                affected += 1

        return affected
