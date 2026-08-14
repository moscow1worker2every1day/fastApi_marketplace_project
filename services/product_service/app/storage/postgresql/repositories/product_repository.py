from typing import List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.storage.postgresql.models.product_model import ProductOrm
from app.log import products_logger


class ProductRepository:

    @staticmethod
    async def get_product_by_id(session: AsyncSession, product_id: UUID) -> ProductOrm:
        # select on load
        query = (
            select(ProductOrm)
            .options(selectinload(ProductOrm.category))
            .where(ProductOrm.id == product_id)
        )
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    async def get_products(
        *,
        session: AsyncSession,
        only_available: bool,
        category_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[ProductOrm]:
        query = (
            select(ProductOrm)
            .options(selectinload(ProductOrm.category))
            .limit(limit)
            .offset(offset)
        )
        if only_available:
            query = query.where(ProductOrm.available.is_(True))

        if category_id:
            query = query.where(ProductOrm.category_id == category_id)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_products_by_ids(session: AsyncSession, product_ids: List[UUID]) -> List[ProductOrm]:
        if not product_ids:
            return []

        query = (
            select(ProductOrm)
            .options(selectinload(ProductOrm.category))
            .where(ProductOrm.id.in_(product_ids))
        )
        result = await session.execute(query)
        products = result.scalars().all()

        return products

    @staticmethod
    async def delete_product(*, session: AsyncSession, product_id: UUID) -> ProductOrm:
        try:
            delete_product = await ProductRepository.get_product_by_id(session=session, product_id=product_id)

            await session.delete(delete_product)
            await session.commit()
            return delete_product
        except Exception as e:
            raise ValueError(f"Cant delete product! Error: {e}")

    @staticmethod
    async def unavailable_product(*, session: AsyncSession, product_id: UUID) -> ProductOrm:
        try:
            query = (
                update(ProductOrm)
                .where(ProductOrm.id == product_id)
                .values(available=False)
                .execution_options(synchronize_session="fetch")
                .returning(ProductOrm)
            )

            result = await session.execute(query)
            await session.flush()
            await session.commit()

            product = result.scalar_one()
            return product

        except Exception as e:
            products_logger.info(f"Cannot unavailable product {e}")
            raise ValueError(f"Cannot unavailable product! Product_id={product_id} dont found")

    @staticmethod
    async def create_new_product(
            *,
            session: AsyncSession,
            name: str,
            description: str | None = None,
            price: float,
            stock: int,
            category_id: UUID,
            seller_id: UUID
    ) -> ProductOrm:
        new_product = ProductOrm(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            seller_id=seller_id
        )
        session.add(new_product)
        await session.flush()
        await session.commit()
        return new_product


    @staticmethod
    async def update_product(
        *,
        session: AsyncSession,
        name: str | None,
        description: str | None,
        price: float,
        stock: int,
        category_id: UUID | None
    ) -> ProductOrm:
        try:
            updated_product = ProductOrm(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id
            )

            await session.flush()
            await session.commit()
            products_logger.info(f"Updated product [{updated_product}]")
            return updated_product
        except Exception as e:
            products_logger.warning(f"Cannot update product {e}")
            raise ValueError(f"Cannot update product {e}")

