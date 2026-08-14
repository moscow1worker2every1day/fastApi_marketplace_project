from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from app.schemas.category import GetCategory, NewCategory, UpdateCategoryDescription
from app.services.category_service import CategoryService
from app.storage.postgresql.connection import SessionDep
from app.dependencies.category_dependency import TargetCategoryDep

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.delete(
    "/{category_id}",
    response_model=GetCategory,
    summary="Delete category",
    description="Delete a category by ID and return the deleted record.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Category not found"},
    },
)
async def delete_category(
    session: SessionDep,
    target_category: TargetCategoryDep,
) -> GetCategory:
    return await CategoryService.delete_category_by_id(
        session=session,
        category_id=target_category.id,
    )


@router.post(
    "/",
    response_model=GetCategory,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description=(
        "Create a new category. "
        "Use `parent_id` to place the category inside an existing hierarchy."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Parent category not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
async def add_category(session: SessionDep, data: NewCategory) -> GetCategory:
    return await CategoryService.create_new_category(
        session=session,
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
    )


@router.put(
    "/{category_id}/description",
    response_model=GetCategory,
    summary="Update category description",
    description="Replace the description of an existing category.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Category not found"},
    },
)
async def update_category_description(
    session: SessionDep,
    target_category: TargetCategoryDep,
    payload: UpdateCategoryDescription,
) -> GetCategory:
    return await CategoryService.update_category_description(
        category_id=target_category.id,
        new_description=payload.description,
        session=session,
    )


@router.get(
    "/{category_id}",
    response_model=GetCategory,
    summary="Get category by ID",
    description="Return a single category by its UUID.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Category not found"},
    },
)
async def get_category(session: SessionDep, category_id: UUID) -> GetCategory:
    return await CategoryService.get_category_by_id(category_id=category_id, session=session)


@router.get(
    "/",
    response_model=List[GetCategory],
    summary="List categories",
    description="Return all categories in the catalog.",
)
async def get_categories(session: SessionDep) -> List[GetCategory]:
    return await CategoryService.get_all_categories(session=session)
