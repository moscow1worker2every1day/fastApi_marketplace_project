from typing import List
from uuid import UUID

from app.storage.postgresql.models.category_model import CategoryOrm

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryRepository:
    @staticmethod
    async def delete_category(*, session: AsyncSession, category_id: UUID) -> CategoryOrm:
        try:
            delete_category = await CategoryRepository.get_category_by_id(category_id=category_id, session=session)
            await session.delete(delete_category)
            await session.commit()
            return delete_category
        except ValueError:
            raise ValueError(f"Невозможно удалить данные! Категория id={category_id} не найдена")

    @staticmethod
    async def get_category_by_id(
        *,
        session: AsyncSession,
        category_id: UUID,
    ) -> CategoryOrm:
        # select on load
        query = select(CategoryOrm).where(CategoryOrm.id == category_id)
        result = await session.execute(query)
        category = result.scalar_one()
        return category

    @staticmethod
    async def get_categories(session: AsyncSession) -> List[CategoryOrm]:
        # select on load
        query = select(CategoryOrm)
        result = await session.execute(query)
        await session.commit()
        categories = result.scalars().all()
        return categories

    @staticmethod
    async def update_category_description(
        *,
        session: AsyncSession,
        category_id: UUID,
        new_description: str,
    ) -> CategoryOrm:
        update_category = await CategoryRepository.get_category_by_id(
            session=session,
            category_id=category_id,
        )
        update_category.description = new_description
        await session.commit()
        await session.refresh(update_category)
        return update_category

    @staticmethod
    async def create_new_category(
        *,
        session: AsyncSession,
        name: str,
        description: str | None = None,
        parent_id: UUID | None = None,
    ) -> CategoryOrm:
        """Create a new category in 'categories' table."""
        new_category = CategoryOrm(
            name=name,
            description=description,
            parent_id=parent_id,
        )
        session.add(new_category)
        await session.flush() #insert into database without closing the transaction and get id
        await session.commit()
        return new_category
