from pydantic import field_validator, BaseModel


class NewCategory(BaseModel):
    name: str
    description: str | None = None
    parent_id: int | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Название не может быть пустым")
        return value

    class Config:
        from_attributes = True


class GetCategory(NewCategory):
    id: int


class UpdateCategory(BaseModel):
    id: int
    description: str

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Описание не может быть пустым")
        return value

    class Config:
        from_attributes = True
