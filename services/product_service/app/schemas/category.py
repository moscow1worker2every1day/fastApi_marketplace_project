from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import EXAMPLE_UUID


class NewCategory(BaseModel):
    name: str = Field(
        min_length=1,
        description="Category display name. Must not be blank.",
        examples=["Electronics"],
    )
    description: str | None = Field(
        default=None,
        description="Optional category description.",
        examples=["Devices, gadgets, and accessories"],
    )
    parent_id: UUID | None = Field(
        default=None,
        description="Parent category UUID. Omit or set to null for a root category.",
        examples=[EXAMPLE_UUID],
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Name must not be blank")
        return value

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Electronics",
                    "description": "Devices, gadgets, and accessories",
                    "parent_id": None,
                },
                {
                    "name": "Smartphones",
                    "description": "Mobile phones and accessories",
                    "parent_id": EXAMPLE_UUID,
                },
            ]
        },
    )


class GetCategory(NewCategory):
    id: UUID = Field(
        description="Unique category identifier.",
        examples=[EXAMPLE_UUID],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": EXAMPLE_UUID,
                    "name": "Electronics",
                    "description": "Devices, gadgets, and accessories",
                    "parent_id": None,
                }
            ]
        },
    )


class UpdateCategoryDescription(BaseModel):
    description: str = Field(
        min_length=1,
        description="New category description. Must not be blank.",
        examples=["Updated category description"],
    )

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Description must not be blank")
        return value

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"description": "Updated description"},
            ]
        },
    )
