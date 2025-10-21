from pydantic import BaseModel, field_validator, EmailStr

class NewUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    @field_validator("first_name")
    @classmethod
    def name_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        return value

    class Config:
        from_attributes = True


class GetUser(NewUser):
    id: int





