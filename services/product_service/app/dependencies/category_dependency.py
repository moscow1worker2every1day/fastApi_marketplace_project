from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from app.services.category_service import CategoryService
from sqlalchemy.exc import NoResultFound

from app.storage.postgresql.connection import SessionDep
from app.storage.postgresql.models.category_model import CategoryOrm
from app.storage.postgresql.repositories.category_repository import CategoryRepository


async def get_target_category(
    category_id: UUID,
    session: SessionDep,
) -> CategoryOrm:
    """Validate category_id and load the category from the database."""
    try:
        category_orm = await CategoryRepository.get_category_by_id(
            session=session,
            category_id=category_id,
        )
        return CategoryService._to_get_category(category_orm)

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id={category_id} not found"
        )

TargetCategoryDep = Annotated[CategoryOrm, Depends(get_target_category)]
