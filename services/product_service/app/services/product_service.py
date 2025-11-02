from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.storage.postgresql.repositories.product_repository import ProductRepository
from app.schemas.product import GetProduct, NewProduct


class ProductService:

    @staticmethod
    async def get_product_by_id(*, session: AsyncSession, product_id: int) -> GetProduct:
        try:
            product_orm = await ProductRepository.get_product_by_id(session=session, product_id=product_id)
            return GetProduct.from_orm(product_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def get_products(*, session: AsyncSession) -> List[GetProduct]:
        try:
            products_orm = await ProductRepository.get_products(session=session, only_available=False)
            return [
                GetProduct.model_validate(product, from_attributes=True)
                for product in products_orm
            ]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def delete_product(*, session: AsyncSession, product_id: int) -> GetProduct:
        try:
            delete_product_orm = await ProductRepository.delete_product(
                session=session,
                product_id=product_id
            )
            return GetProduct.from_orm(delete_product_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def create_new_product(*, session: AsyncSession, new_product: NewProduct) -> GetProduct:
        try:
            new_product_orm = await ProductRepository.create_new_product(
                name=new_product.name,
                description=new_product.description,
                price=new_product.price,
                stock=new_product.stock,
                category_id=new_product.category_id,
                session=session)
            return GetProduct.from_orm(new_product_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )