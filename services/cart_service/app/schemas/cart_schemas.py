from uuid import UUID

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    quantity: int = Field(
        description="Quantity of the cart item.",
        default=1,
        ge=1,
    )
    price: float = Field(
        description="Price of the cart item.",
        default=0.0,
        ge=0.0,
    )


class UserCartItem(CartItem):
    product_id: UUID = Field(
        description="ID of the product.",
        default=None,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "quantity": 2,
                    "price": 3599.99,
                }
            ]
        }
    }


class UserCart(BaseModel):
    items: list[UserCartItem] = Field(
        description="List of cart items.",
        default_factory=list,
    )
    total: float = Field(
        description="Total price of the cart items.",
        default=0.0,
        ge=0.0,
        alias="total_price",
    )


class UserCartOut(UserCart):
    message: str | None = Field(
        description="Message of the cart operation.",
        default=None,
    )
