from uuid import UUID

from fastapi import APIRouter, status

from app.schemas.cart_schemas import UserCart, UserCartItem, UserCartOut
from app.services.cart_service import UserCartService
from app.enums import DeltaEnum

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/{user_id}", response_model=UserCart, status_code=status.HTTP_200_OK)
async def get_cart(user_id: UUID) -> UserCart:
    return await UserCartService.get_user_cart(user_id=user_id)


@router.put("/{user_id}/change/{product_id}", response_model=UserCart)
async def change_quantity(user_id: UUID, product_id: UUID, delta: DeltaEnum) -> UserCartOut:
    cart = await UserCartService.change_item_quantity(
        user_id=user_id,
        product_id=product_id,
        delta=delta,
    )
    return UserCartOut(message="Quantity changed", items=cart.items, total=cart.total)


@router.post("/{user_id}/{product_id}", response_model=UserCartOut, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    user_id: UUID,
    product_id: UUID,
    item: UserCartItem,
) -> UserCartOut:
    cart = await UserCartService.add_to_user_cart(
        user_id=user_id,
        product_id=product_id,
        price=item.price,
        quantity=item.quantity,
    )
    return UserCartOut(message="Item added", items=cart.items, total=cart.total)


@router.delete("/{user_id}/remove/{product_id}", response_model=UserCartOut, status_code=status.HTTP_200_OK)
async def remove_from_cart(user_id: UUID, product_id: UUID) -> UserCartOut:
    cart = await UserCartService.delete_from_user_cart(
        user_id=user_id,
        product_id=product_id,
    )
    return UserCartOut(message="Item deleted", items=cart.items, total=cart.total)


@router.delete("/{user_id}/clear", response_model=UserCartOut, status_code=status.HTTP_200_OK)
async def clear_cart(user_id: UUID) -> UserCartOut:
    cart = await UserCartService.clear_user_cart(user_id=user_id)
    return UserCartOut(message="Cart cleared", items=cart.items, total=cart.total)
