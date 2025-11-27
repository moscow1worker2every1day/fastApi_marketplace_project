import json

from app.storage.redis.connection import redis_connection, RedisService


class CartRepository:
    @staticmethod
    async def get_cart(user_id: int) -> dict | None:
        key = await RedisService.get_cart_key(user_id)
        cart = await redis_connection.get(key)
        if not cart:
            return None
        return dict(json.loads(cart))

    @staticmethod
    async def add_to_cart(user_id: int,
                          product_id: int,
                          price: float,
                          quantity: int = 1) -> dict | None:
        key = await RedisService.get_cart_key(user_id)
        cart_data = await redis_connection.get(key)
        if not cart_data:
            return None

        cart = json.loads(cart_data)

        found = False
        for existing_item in cart["items"]:
            if existing_item["product_id"] == product_id:
                existing_item["quantity"] += quantity
                cart["total"] += price * quantity
                found = True
                break
        if not found:
            cart["items"].append(dict({product_id: int,
                                       quantity: int,
                                       price: float}))
            cart["total"] += price * quantity

        await redis_connection.set(key, json.dumps(cart))
        return cart

    @staticmethod
    async def delete_from_cart(user_id: int, product_id: int) -> dict | None:
        key = await RedisService.get_cart_key(user_id)
        cart_data = await redis_connection.get(key)
        if not cart_data:
            return None

        cart = json.loads(cart_data)
        cart["items"] = [i for i in cart["items"] if i["product_id"] != product_id]

        cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"]) if cart["items"] else 0.0

        await redis_connection.set(key, json.dumps(cart))
        return cart

    @staticmethod
    async def clear_cart(user_id: int) -> dict:
        key = await RedisService.get_cart_key(user_id)
        await redis_connection.delete(key)
        cart = {"items": [], "total": 0.0}
        return cart
