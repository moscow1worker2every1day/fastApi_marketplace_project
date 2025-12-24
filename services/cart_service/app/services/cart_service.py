import asyncio
from fastapi import HTTPException, status
from redis.exceptions import RedisError
from app.schemas.cart_schemas import UserCart, UserCartItem
from app.storage.redis.repositories.cart_repository import CartRepository


class UserCartService:

    @staticmethod
    async def get_user_cart(user_id: int) -> UserCart:
        try:
            cart = await CartRepository.get_cart(user_id=user_id)
        except RedisError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Please try again in 5 minutes"
            )
        if cart is None:
            return UserCart(items=[], total=0.0)
        print(cart)
        return UserCart(**cart)

    @staticmethod
    async def change_item_quantity(user_id: int, product_id: int, delta: int):
        try:
            cart = await CartRepository.change_quantity(user_id=user_id, product_id=product_id, delta=delta)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e))
        if cart is None:
            return UserCart(
                items=[],
                total=0.0)
        return UserCart(**cart)

    @staticmethod
    async def add_to_user_cart(user_id: int, product_id: int, price: float, quantity: int) -> UserCart:
        cart = await CartRepository.add_to_cart(user_id=user_id,
                                                product_id=product_id,
                                                price=price,
                                                quantity=quantity)
        if cart is None:
            return UserCart(
                items=[UserCartItem(
                    product_id=product_id,
                    price=price,
                    quantity=quantity)],
                total=0.0)
        return UserCart(**cart)

    @staticmethod
    async def delete_from_user_cart(user_id: int, product_id: int) -> UserCart:
        cart = await CartRepository.delete_from_cart(user_id=user_id, product_id=product_id)
        if cart is None:
            return UserCart(items=[], total=0.0)
        return UserCart(**cart)

    @staticmethod
    async def clear_user_cart(user_id: int) -> UserCart:
        asyncio.create_task(CartRepository.clear_cart(user_id=user_id))
        return UserCart(items=[], total=0.0)

    @staticmethod
    async def update_cart_products(product_id: int, price: float, available: bool):
        await CartRepository.update_products()
