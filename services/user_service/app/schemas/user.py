from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional

class NewUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("Имя и фамилия не может быть пустым")
        return value

    class Config:
        from_attributes = True


class GetUser(NewUser):
    id: int


class UpdateName(BaseModel):

    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("first_name", "last_name")
    def not_empty(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Имя и фамилия не может быть пустым")
        return value

    class Config:
        from_attributes = True


class UpdateEmail(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


