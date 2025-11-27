import json
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.schemas.cart_schemas import UserCart, UserCartItem
from app.services.cart_service import UserCartService
from app.storage.redis.connection import RedisService, redis_connection


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/{user_id}", response_model=UserCart)
async def get_cart(user_id: int) -> UserCart:
    cart = await UserCartService.get_user_cart(user_id=user_id)
    return cart


@router.post("/{user_id}/{product_id}", response_model=Dict)
async def add_to_cart(user_id: int, item: UserCartItem) -> Dict:
    cart = UserCartService.add_to_user_cart(user_id=user_id,
                                            product_id=item.product_id,
                                            price=item.price,
                                            quantity=item.quantity)
    return {"message": "Item added", "cart": cart}


@router.delete("/{user_id}/remove/{product_id}")
async def remove_from_cart(user_id: int, product_id: int) -> Dict:
    cart = UserCartService.delete_from_user_cart(user_id=user_id,
                                                 product_id=product_id)
    return {"message": "Item removed", "cart": cart}


@router.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: int) -> Dict:
    cart = UserCartService.clear_user_cart(user_id=user_id)
    return {"message": "Cart cleared", "cart": cart}
