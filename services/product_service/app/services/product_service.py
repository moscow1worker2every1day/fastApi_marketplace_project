from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import DeleteProductMode
from app.storage.postgresql.models.product_model import ProductOrm
from app.log import products_logger
from app.storage.postgresql.repositories.product_repository import ProductRepository
from app.schemas.product import GetProduct


class ProductService:

    @staticmethod
    def _to_get_product(orm: ProductOrm) -> GetProduct:
        return GetProduct.model_validate(orm, from_attributes=True)

    @staticmethod
    async def get_product_by_id(
        *,
        session: AsyncSession,
        target_product: GetProduct,
    ) -> GetProduct:
        product_orm = await ProductRepository.get_product_by_id(
            session=session,
            product_id=target_product.id,
        )
        return ProductService._to_get_product(product_orm)

    @staticmethod
    async def get_products(
        *,
        session: AsyncSession,
        only_available: bool,
        category_id: UUID | None,
        limit: int,
        offset: int,
    ) -> List[GetProduct]:
        products_orm = await ProductRepository.get_products(
            session=session,
            only_available=only_available,
            category_id=category_id,
            limit=limit,
            offset=offset,
        )
        return [
            ProductService._to_get_product(product)
            for product in products_orm
        ]

    @staticmethod
    async def delete_product(
        *,
        session: AsyncSession,
        product_id: int,
        mode: DeleteProductMode,
    ) -> GetProduct:
        try:
            delete_operation = {
                DeleteProductMode.DELETE: ProductRepository.delete_product,
                DeleteProductMode.SOFT: ProductRepository.unavailable_product,
            }
            delete_product_orm = await delete_operation[mode](
                session=session,
                product_id=product_id,
            )
            # await Publisher.publish_product_change(delete_product_orm, f"product.delete.{mode}")
            return ProductService._to_get_product(delete_product_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def create_new_product(
        *,
        session: AsyncSession,
        name: str,
        description: str | None,
        price: float,
        stock: int,
        category_id: UUID,
        seller_id: UUID,
    ) -> GetProduct:
        try:
            new_product_orm = await ProductRepository.create_new_product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category_id=category_id,
                seller_id=seller_id,
                session=session
            )
            # await Publisher.publish_product_change(product, "create")
            return ProductService._to_get_product(new_product_orm)
        
        except IntegrityError as e:
            if "products_category_id_fkey" in str(e.orig):
                products_logger.info(f"Cannot insert product: {type(e).__name__} - {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {category_id} not found"
                )
            else:
                products_logger.warning(f"Cannot insert product: {type(e).__name__} - {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot insert product {type(e).__name__} - {e}"
                )
        except Exception as e:
            products_logger.error(f"Cannot insert product: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot insert product: {type(e).__name__} - {e}"
            )
