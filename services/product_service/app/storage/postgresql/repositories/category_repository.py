from typing import List, Optional, Dict

from app.storage.postgresql.models.category_model import CategoryOrm

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.logging import logging


class CategoryRepository:
    @staticmethod
    async def delete_category(session: AsyncSession, category_id: int) -> CategoryOrm:
        try:
            delete_category = await CategoryRepository.get_category_by_id(category_id=category_id, session=session)
            await session.delete(delete_category)
            await session.commit()
            return delete_category
        except ValueError:
            raise ValueError(f"Невозможно удалить данные! Пользователь с id={category_id} не найден")

    @staticmethod
    async def get_category_by_id(session: AsyncSession, category_id: int) -> CategoryOrm:
        try:
            query = select(CategoryOrm).where(CategoryOrm.id == category_id)
            result = await session.execute(query)
            category = result.scalar_one()
            return category
        except NoResultFound:
            raise ValueError(f"Категория id={category_id} не найдена")

    @staticmethod
    async def get_categories(session: AsyncSession) -> List[CategoryOrm]:
        query = select(CategoryOrm)
        result = await session.execute(query)
        await session.commit()
        categories = result.scalars().all()
        return categories

    @staticmethod
    async def update_category_description(session: AsyncSession, id: int, new_description: str) -> CategoryOrm:
        try:
            update_category = await CategoryRepository.get_category_by_id(category_id=id, session=session)

            update_category.description = new_description
            await session.commit()
            await session.refresh(update_category)
            return update_category
        except IntegrityError as e:
            raise ValueError(f"Невозможно обновить description! Ошибка {e}")
        except ValueError as e:
            raise ValueError(f"Невозможно обновить description! {e}")


    @staticmethod
    async def create_new_category(
            session: AsyncSession,
            name: str,
            description: str | None = None,
            parent_id: int | None = None
            ) -> CategoryOrm:
        try:
            new_category = CategoryOrm(
                name=name,
                description=description,
                parent_id=parent_id,
            )
            session.add(new_category)
            await session.flush() #занести изм в бд предварительно и получить id
            await session.commit()
            logging.info(f"Inserted category [{new_category.id}] {name}: parent_id {parent_id}")
            return new_category
        except IntegrityError as e:
            error_msg = str(e.orig)
            if "categories_name_key" in error_msg:
                logging.info(f"Cannot insert category {name}: category name must be unique")
                raise ValueError(f"Нельзя создать категорию! Название name={name} нарушает ограничение уникальности")
            elif "categories_parent_id_fkey" in error_msg:
                logging.info(f"Cannot insert category {name}: parent_id {parent_id} does not exist")
                raise ValueError(f"Нельзя создать категорию! Корневой категории id={parent_id} не существует")
            else:
                logging.warning(f"Cannot insert category name={name} "
                                f"description={description} parent_id={parent_id} "
                                f"unknown error")
                raise ValueError(f"Нельзя создать категорию!")