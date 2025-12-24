from pydantic import BaseModel, field_validator, EmailStr
from pydantic.config import ConfigDict
from fastapi import Form
from typing import Optional, Annotated


class BaseUser(BaseModel):
    first_name: Annotated[str, Form()]
    last_name: Annotated[str, Form()]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"first_name": "Anastasia",
                 "last_name": "Marti",
                 }]})

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("Имя и фамилия не может быть пустым")
        return value


class NewUser(BaseUser):
    password: str
    email: EmailStr
    active: bool | None = True
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"first_name": "Anastasia",
                 "last_name": "Marti",
                 "password": "pass",
                 "email": "string@mail.ru",
                 }]})


class GetUser(BaseUser):
    id: int


class GetNewUser(GetUser):
    hashed_password: str



class UpdateUserName(BaseUser):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateUserEmail(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
