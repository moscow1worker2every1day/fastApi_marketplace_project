from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr
from pydantic.config import ConfigDict
from fastapi import Form
from typing import Annotated

from app.config import UserRoles


class BaseUser(BaseModel):
    first_name: Annotated[str, Form()]
    last_name: Annotated[str, Form()]
    email: EmailStr
    role: UserRoles = UserRoles.user

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
            raise ValueError("Name and Surname must be not blanck")
        return value


class NewUser(BaseUser):
    password: str
    active: bool | None = True
    model_config = ConfigDict(
        #strict=True,  # строгое соответсвие полям
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"first_name": "Anast",
                 "last_name": "Marti",
                 "password": "pass",
                 "email": "st@mail.ru",
                 }]})


class GetUser(BaseUser):
    updated_at: datetime
    created_at: datetime
    hashed_password: str
    id: int
    active: bool


class UpdateUserName(BaseUser):
    id: int
    first_name: str | None = None
    last_name: str | None = None


class UpdateUserEmail(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
