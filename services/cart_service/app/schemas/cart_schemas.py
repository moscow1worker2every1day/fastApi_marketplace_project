from pydantic import BaseModel, field_validator
from enum import Enum


class UserCartItem(BaseModel):
    product_id: int
    quantity: int
    price: float

    @field_validator("quantity")
    @classmethod
    def value_is_positive(cls, value):
        if value <= 0:
            raise ValueError("Value must be > 0")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": "1",
                    "quantity": "2",
                    "price": 3599.99
                }
            ]
        }
    }


class UserCart(BaseModel):
    items: list[UserCartItem]
    total: float


class UserCartOut(UserCart):
    message: str | None


class DeltaEnum(int, Enum):
    increase = 1
    decrease = -1
