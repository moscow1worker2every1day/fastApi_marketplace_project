import json
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.schemas.cart_schemas import UserCart, UserCartItem
from app.storage.redis.connection import RedisService, redis_connection


router = APIRouter(prefix="/cart", tags=["Products"])


@router.get("/{user_id}", response_model=UserCart)
async def get_cart(user_id: int) -> Dict:
    key = await RedisService.get_cart_key(user_id)
    cart = await redis_connection.get(key)
    if not cart:
        return {"items": [], "total": 0.0}

    return json.loads(cart)


@router.post("/{user_id}/add")
async def add_to_cart(user_id: int, item: UserCartItem) -> Dict:
    key = await RedisService.get_cart_key(user_id)
    cart_data = await redis_connection.get(key)
    if cart_data:
        cart = json.loads(cart_data)
    else:
        cart = {"items": [], "total": 0.0}

    found = False
    for existing_item in cart["items"]:
        if existing_item["product_id"] == item.product_id\
                and existing_item["price"] == item.price:
            existing_item["quantity"] += item.quantity
            cart["total"] += item.price * item.quantity
            found = True
            break
    if not found:
        cart["items"].append(item.dict())
        cart["total"] += item.price * item.quantity

    await redis_connection.set(key, json.dumps(cart))
    return {"message": "Item added", "cart": cart}


@router.delete("/cart/{user_id}/remove/{product_id}")
async def remove_from_cart(user_id: int, product_id: int) -> Dict:
    key = await RedisService.get_cart_key(user_id)
    cart_data = await redis_connection.get(key)
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart = json.loads(cart_data)

    cart["items"] = [i for i in cart["items"] if i["product_id"] != product_id]

    cart["total"] = sum(item["price"] * item["quantity"] for item in cart["items"]) if cart["items"] else 0.0

    await redis_connection.set(key, json.dumps(cart))
    return {"message": "Item removed", "cart": cart}


@router.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: int) -> Dict:
    key = await RedisService.get_cart_key(user_id)
    await redis_connection.delete(key)
    cart = {"items": [], "total": 0.0}
    return {"message": "Cart cleared", "cart": cart}
