from pydantic import field_validator, BaseModel, model_validator


class NewProduct(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int
    category_id: int

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Название не может быть пустым")
        return value

    @field_validator("price", "stock")
    @classmethod
    def value_is_positive(cls, value):
        if value <= 0:
            raise ValueError("Значение должно быть > 0")
        return value

    class Config:
        from_attributes = True


class GetProduct(NewProduct):
    id: int
    available: bool
