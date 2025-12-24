from typing import Dict, Annotated

from fastapi import APIRouter, Body, status

from app.schemas.cart_schemas import UserCart, UserCartItem, UserCartOut, DeltaEnum
from app.services.cart_service import UserCartService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/{user_id}", response_model=UserCart, status_code=status.HTTP_200_OK)
async def get_cart(user_id: int) -> UserCart:
    cart = await UserCartService.get_user_cart(user_id=user_id)
    return cart


@router.put("/{user_id}/change/{product_id}", response_model=UserCart)
async def change_quantity(user_id: int, product_id: int, delta: DeltaEnum):
    cart = await UserCartService.change_item_quantity(
        user_id=user_id,
        product_id=product_id,
        delta=delta
    )
    return cart


@router.post("/{user_id}/{product_id}", response_model=UserCartOut)
async def add_to_cart(user_id: int, item: Annotated[UserCartItem, Body(embed=True)]) -> UserCartOut:
    cart = await UserCartService.add_to_user_cart(user_id=user_id, **item.dict())
    return UserCartOut(message="Item added", **cart.dict())


@router.delete("/{user_id}/remove/{product_id}")
async def remove_from_cart(user_id: int, product_id: int) -> dict:
    cart = await UserCartService.delete_from_user_cart(
        user_id=user_id,
        product_id=product_id
    )
    return {"message": "Item deleted", "cart": cart}


@router.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: int) -> Dict:
    cart = await UserCartService.clear_user_cart(user_id=user_id)
    return {"message": "Cart cleared", "cart": cart}
