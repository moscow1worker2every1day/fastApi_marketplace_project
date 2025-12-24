import json

from app.storage.redis.connection import RedisService
from redis.exceptions import ConnectionError, TimeoutError, RedisError


def get_cart_key(user_id: int) -> str:
    return f"cart:{user_id}"


class CartRepository:

    @staticmethod
    async def get_cart(user_id: int) -> dict | None:
        key = get_cart_key(user_id)
        print(key)
        try:
            cart = await RedisService.get_connection().get(key)
        except (ConnectionError, TimeoutError) as e:
            raise RedisError(f"Error redis: {e}")
        print(cart)

        if not cart:
            return None
        print(json.loads(cart))
        return json.loads(cart)

    @staticmethod
    async def change_quantity(user_id: int, product_id: int, delta: int):
        key = get_cart_key(user_id)

        try:
            redis = RedisService.get_connection()
            cart_data = await redis.get(key)
        except Exception as e:
            raise Exception(f"Error redis: {e}")
        print(cart_data)

        if not cart_data:
            return None

        cart = json.loads(cart_data.decode() if isinstance(cart_data, bytes) else cart_data)

        updated = False
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += delta
                if item["quantity"] <= 0:
                    cart["items"].remove(item)
                updated = True
                break
        # если товара нет в корзине
        if not updated:
            raise ValueError(f"Товара {product_id} нет в корзине")

        # Пересчитываем total
        cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"])

        # Сохраняем в Redis
        await redis.set(key, json.dumps(cart))
        return cart

    @staticmethod
    async def add_to_cart(user_id: int,
                          product_id: int,
                          price: float,
                          quantity: int = 1) -> dict | None:
        key = get_cart_key(user_id)
        print(key)
        try:
            redis = RedisService.get_connection()
            cart_data = await redis.get(key)
        except Exception as e:
            raise Exception(f"Error redis: {e}")
        print(cart_data)

        if not cart_data:
            cart = {
                "items": [{"product_id": product_id, "price": price, "quantity": quantity}],
                "total": price * quantity
            }
            await redis.set(key, json.dumps(cart))
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
            cart["items"].append({"product_id": product_id,
                                  "price": price,
                                  "quantity": quantity})
            cart["total"] += price * quantity
        print(cart)
        await redis.set(key, json.dumps(cart))
        return cart

    @staticmethod
    async def delete_from_cart(user_id: int, product_id: int) -> dict | None:
        key = get_cart_key(user_id)
        cart_data = await RedisService.get_connection().get(key)
        if not cart_data:
            return None

        cart = json.loads(cart_data)
        cart["items"] = [i for i in cart["items"] if i["product_id"] != product_id]

        cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"]) if cart["items"] else 0.0

        await RedisService.get_connection().set(key, json.dumps(cart))
        return cart

    @staticmethod
    async def clear_cart(user_id: int) -> None:
        key = get_cart_key(user_id)
        await RedisService.get_connection().delete(key)
