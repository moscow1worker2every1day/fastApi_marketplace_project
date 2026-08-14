from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.log import categories_logger
from app.schemas.category import GetCategory
from app.storage.postgresql.models.category_model import CategoryOrm
from app.storage.postgresql.repositories.category_repository import CategoryRepository


class CategoryService:
    """Service for managing categories."""

    @staticmethod
    def _to_get_category(orm: CategoryOrm) -> GetCategory:
        """Convert CategoryOrm (SQLAlchemy ORM model) to GetCategory (Pydantic schema)."""
        return GetCategory.model_validate(orm, from_attributes=True)

    @staticmethod
    async def update_category_description(
        *,
        category_id: UUID,
        new_description: str,
        session: AsyncSession,
    ) -> GetCategory:
        """Update the description of a category."""
        try:
            updated_category_orm = await CategoryRepository.update_category_description(
                session=session,
                category_id=category_id,
                new_description=new_description
            )
            return CategoryService._to_get_category(updated_category_orm)
        except IntegrityError as e:
            categories_logger.warning(f"Cannot update category description: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update category description: {type(e).__name__} - {e}"
            )
        except Exception as e:
            categories_logger.error(f"Unexpected error: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot update category description: {type(e).__name__} - {e}"
            )

    @staticmethod
    async def get_all_categories(session: AsyncSession) -> List[GetCategory]:
        categories_orm = await CategoryRepository.get_categories(session)
        if not categories_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Categories not found")
            )
        return [GetCategory.from_orm(cat) for cat in categories_orm]

    @staticmethod
    async def get_category_by_id(session: AsyncSession, category_id: int) -> GetCategory:
        try:
            category_orm = await CategoryRepository.get_category_by_id(session=session, category_id=category_id)
            return GetCategory.from_orm(category_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def delete_category_by_id(id: int, session: AsyncSession) -> GetCategory:
        try:
            deleted_category_orm = await CategoryRepository.delete_category(category_id=id, session=session)
            return GetCategory.from_orm(deleted_category_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def create_new_category(
        *,
        session: AsyncSession,
        name: str,
        description: str | None,
        parent_id: int | None,
    ) -> GetCategory:
        """Create a new category in 'categories' table."""
        categories_logger.info(f"Creating new category: name={name}, description={description}, parent_id={parent_id}")
        try:
            new_category_orm = await CategoryRepository.create_new_category(
                session=session,
                name=name,
                description=description,
                parent_id=parent_id
            )
            categories_logger.info(
                f"New category created: id={new_category_orm.id}, name={name}, "
                f"description={description}, parent_id={parent_id}"
            )
            return CategoryService._to_get_category(new_category_orm)
        except IntegrityError as e:
            error_msg = str(e.orig)
            if "categories_name_key" in error_msg:
                categories_logger.warning(f"Cannot insert category {name}: category name must be unique")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot insert category {name}: category name must be unique"
                )

            if "categories_parent_id_fkey" in error_msg:
                categories_logger.warning(f"Cannot insert category {name}: parent_id {parent_id} does not exist")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot insert category '{name}': parent_id {parent_id} does not exist"
                )
            
            categories_logger.warning(
                f"Cannot insert category name={name} "
                f"description={description} parent_id={parent_id} "
                f"unknown error: {type(e).__name__} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot insert category '{name}': unknown error: {type(e).__name__} - {str(e)}"
            )
        except Exception as e:
            categories_logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {type(e).__name__} - {str(e)}"
            )