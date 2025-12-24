from fastapi import APIRouter
from app.schemas.order_schema import BaseOrder, OrderOut

router = APIRouter(prefix="/order")


@router.get("/{order_id}",
            tags=["orders"],
            summary="Get one user order",
            description="Get one user order with all the information, name, description, total_price, time",
            response_description="The get order"
            )
async def get_order(order_id: int):
    return {"message": f"{order_id}"}


@router.post("/{user_id}")
async def create_order(user_id: int, order: BaseOrder):
    """Создание заказа со всей информацией"""
    pass
