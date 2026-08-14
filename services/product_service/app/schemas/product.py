from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import EXAMPLE_UUID


class NewProduct(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Product name. Must be between 1 and 100 characters.",
        examples=["iPhone 15 Pro"],
    )
    description: str | None = Field(
        default=None,
        max_length=1024,
        description="Optional product description. Max 1024 characters.",
        examples=["256 GB, titanium finish"],
    )
    price: float = Field(
        gt=0,
        description="Product price. Must be greater than 0.",
        examples=[1299.99],
    )
    stock: int = Field(
        gt=0,
        description="Available stock quantity. Must be greater than 0.",
        examples=[10],
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be blank")
        return value

    @field_validator("price", "stock")
    @classmethod
    def value_is_positive(cls, value):
        if value <= 0:
            raise ValueError("Value must be > 0")
        return value

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "iPhone 15 Pro",
                    "description": "256 GB, titanium finish",
                    "price": 1299.99,
                    "stock": 10,
                }
            ]
        },
    )


class GetProduct(NewProduct):
    id: UUID = Field(
        description="Unique product identifier.",
        examples=[EXAMPLE_UUID],
    )
    available: bool = Field(
        description="Whether the product is available for purchase.",
        examples=[True],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": EXAMPLE_UUID,
                    "name": "iPhone 15 Pro",
                    "description": "256 GB, titanium finish",
                    "price": 1299.99,
                    "stock": 10,
                    "available": True,
                }
            ]
        },
    )


# USER_SERVICE SCHEMAS
class GetSeller(BaseModel):
    id: UUID = Field(
        description="Seller user identifier from User Service.",
        examples=[EXAMPLE_UUID],
    )
    role: str = Field(
        description="User role. Must be `seller` for product creation.",
        examples=["seller"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )
