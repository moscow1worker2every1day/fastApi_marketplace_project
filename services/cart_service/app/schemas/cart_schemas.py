from typing import List

from pydantic import BaseModel


class UserCartItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class UserCart(BaseModel):
    items: List[UserCartItem]
    total: float
