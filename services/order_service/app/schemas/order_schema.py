import datetime
from uuid import UUID

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None
    price: float
    stock: int
    category_id: UUID

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Iphone",
                    "description": "Iphone 12 Pro Max 256GB",
                    "price": 135990.99,
                    "stock": 1,
                    "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ]
        }
    }


class BaseOrder(BaseModel):
    description: str | None
    total_price: float
    order_items: list[Item]


class OrderOut(BaseOrder):
    id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
