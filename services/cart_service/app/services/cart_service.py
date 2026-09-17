from uuid import UUID

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.schemas.cart_schemas import UserCart
from app.storage.redis.repositories.cart_repository import CartRepository
from app.log import cart_logger


class UserCartService:

    @staticmethod
    async def get_user_cart(user_id: UUID) -> UserCart:
        try:
            cart: dict | None = await CartRepository.get_cart(user_id=user_id)

        except RedisError as e:
            cart_logger.error("Redis is unavailable: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis is unavailable. Please try again later.",
            )

        if cart is None:
            return UserCart(items=[], total=0.0)

        cart_logger.info("User cart retrieved: %s", cart)
        return UserCart(**cart)

    @staticmethod
    async def change_item_quantity(user_id: UUID, product_id: UUID, delta: int) -> UserCart:
        try:
            cart = await CartRepository.change_quantity(
                user_id=user_id,
                product_id=product_id,
                delta=delta,
            )
        except ValueError as e:
            cart_logger.error("Product %s not found in cart: %s", product_id, e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found in cart",
            ) from e

        if cart is None:
            return UserCart(items=[], total=0.0)

        cart_logger.info("Item quantity changed: %s", cart)
        return UserCart(**cart)

    @staticmethod
    async def add_to_user_cart(
        user_id: UUID,
        product_id: UUID,
        price: float,
        quantity: int,
    ) -> UserCart:
        cart = await CartRepository.add_to_cart(
            user_id=user_id,
            product_id=product_id,
            price=price,
            quantity=quantity,
        )
        cart_logger.info("Item added to cart: %s", cart)
        return UserCart(**cart)

    @staticmethod
    async def delete_from_user_cart(user_id: UUID, product_id: UUID) -> UserCart:
        cart = await CartRepository.delete_from_cart(
            user_id=user_id,
            product_id=product_id,
        )
        if cart is None:
            cart_logger.error("Product %s not found in cart", product_id)
            return UserCart(items=[], total=0.0)

        cart_logger.info("Item removed from cart: %s", cart)
        return UserCart(**cart)

    @staticmethod
    async def clear_user_cart(user_id: UUID) -> UserCart:
        await CartRepository.clear_cart(user_id=user_id)
        cart_logger.info("Cart cleared for user: %s", user_id)
        return UserCart(items=[], total=0.0)

    @staticmethod
    async def handle_product_event(
        *,
        product_id: UUID,
        event: str,
        price: float | None = None,
        available: bool | None = None,
    ) -> int:
        if event in {"product.deleted", "product.unavailable"} or available is False:
            cart_logger.info("Product %s deleted or unavailable, removing from all carts", product_id)
            return await CartRepository.remove_product_from_all_carts(product_id)

        if event == "product.updated":
            cart_logger.info("Product %s updated: %s", product_id, price)
            return await CartRepository.update_product_in_all_carts(
                product_id,
                price=price,
                available=available,
            )
        
        cart_logger.warning("Unknown product event: %s", event)
        return 0
