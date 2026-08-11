from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic.config import ConfigDict
from fastapi import Form
from typing import Annotated

from app.enums import UserRoles


class BaseUser(BaseModel):
    first_name: Annotated[str, Form()]
    last_name: Annotated[str, Form()]
    email: EmailStr
    role: UserRoles = UserRoles.user

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "first_name": "Anastasia",
                    "last_name": "Marti",
                    "email": "st@mail.ru",
                    "role": "user",
                    "active": True
                }
            ]
        }
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("Name and Surname must be not blanck")
        return value


class NewUser(BaseUser):
    password: str
    model_config = ConfigDict(
        #strict=True,  # строгое соответсвие полям
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "first_name": "Anast",
                    "last_name": "Marti",
                    "email": "1@mail.ru",
                    "password": "1",
                    "role": "user",
                }
            ],
            "required": ["first_name", "last_name", "email", "password"]
        }
    )


class GetUser(BaseUser):
    updated_at: datetime
    created_at: datetime
    id: UUID
    active: bool
    hashed_password: str = Field(exclude=True)


class UpdateUserName(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UpdateUserEmail(BaseModel):
    id: UUID
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True
    )

class ResponseMessage(BaseModel):
    user_id: UUID
    message: str