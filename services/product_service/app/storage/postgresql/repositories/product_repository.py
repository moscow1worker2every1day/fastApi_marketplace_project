from typing import List
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.storage.postgresql.models.product_model import ProductOrm
from app.logging import logging


class ProductRepository:

    @staticmethod
    async def get_product_by_id(session: AsyncSession, product_id: int) -> ProductOrm:
        try:
            # select on load
            query = (
                select(ProductOrm)
                .options(selectinload(ProductOrm.category))
                .where(ProductOrm.id == product_id)
            )
            result = await session.execute(query)
            product = result.scalar_one()
            return product
        except NoResultFound:
            raise ValueError(f"Product_id={product_id} dont found")

    @staticmethod
    async def get_products(session: AsyncSession, only_available: bool = True) -> list[ProductOrm]:
        query = (
            select(ProductOrm)
            .options(selectinload(ProductOrm.category))
        )

        if only_available:
            query = query.where(ProductOrm.available.is_(True))

        result = await session.execute(query)

        scalars = result.scalars()
        products: list[ProductOrm] = scalars.all()

        return products

    @staticmethod
    async def get_products_by_ids(session: AsyncSession, product_ids: List[int]) -> List[ProductOrm]:
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
    async def delete_product(*, session: AsyncSession, product_id: int) -> ProductOrm:
        try:
            delete_product = await ProductRepository.get_product_by_id(session=session, product_id=product_id)

            await session.delete(delete_product)
            await session.commit()
            return delete_product
        except Exception as e:
            raise ValueError(f"Cant delete product! Error: {e}")

    @staticmethod
    async def unavailable_product(*, session: AsyncSession, product_id: int) -> ProductOrm:
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
            logging.info(f"Cannot unavailable product {e}")
            raise ValueError(f"Cannot unavailable product! Product_id={product_id} dont found")

    @staticmethod
    async def create_new_product(
            *,
            session: AsyncSession,
            name: str,
            description: str | None = None,
            price: float,
            stock: int,
            category_id: int
    ) -> ProductOrm:
        try:
            new_product = ProductOrm(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id
            )
            session.add(new_product)
            await session.flush()
            await session.commit()
            logging.info(f"Inserted product [{new_product}]")
            return new_product

        except IntegrityError as e:

            if "products_category_id_fkey" in str(e.orig):
                logging.info(f"Cannot insert product {e.params} {e.orig}")
                raise ValueError(f"Cannot insert product: category_id {category_id} dont found")
            else:
                logging.warning(f"Cannot insert product {e.params}. Unknown error: {str(e.orig)}")
                raise ValueError(f"Cannot insert product {e.params}")

    @staticmethod
    async def update_product(*,
                             session: AsyncSession,
                             name: str | None,
                             description: str | None,
                             price: float,
                             stock: int,
                             category_id: int | None) -> ProductOrm:
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
            logging.info(f"Updated product [{updated_product}]")
            return updated_product
        except Exception as e:
            logging.warning(f"Cannot update product {e}")
            raise ValueError(f"Cannot update product {e}")

