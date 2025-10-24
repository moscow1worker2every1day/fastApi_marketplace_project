from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.category import NewCategory, GetCategory
from app.storage.postgresql.repositories.category_repository import CategoryRepository


class CategoryService:
    @staticmethod
    async def update_category_description(category_id: int,
                                          new_description: str,
                                          session: AsyncSession
                                          ) -> GetCategory:
        try:
            updated_category_orm = await CategoryRepository.update_category_description(
                session=session,
                id=category_id,
                new_description=new_description
            )
            return GetCategory.from_orm(updated_category_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def get_all_categories(session: AsyncSession) -> List[GetCategory]:
        categories_orm = await CategoryRepository.get_categories(session)
        if not categories_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Пользователей нет")
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
    async def create_new_category(session: AsyncSession, name: str, description: str, parent_id: int) -> GetCategory:
        try:
            new_user_orm = await CategoryRepository.create_new_category(
                session=session,
                name=name,
                description=description,
                parent_id=parent_id
            )
            return GetCategory.from_orm(new_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )