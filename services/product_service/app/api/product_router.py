from typing import List
from fastapi import APIRouter, Depends

from app.schemas.product import GetProduct, NewProduct
from app.services.product_service import ProductService
from app.storage.postgresql.connection import SessionFactory, get_session


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}", response_model=GetProduct)
async def get_product(product_id: int, session: SessionFactory = Depends(get_session)):
    product = await ProductService.get_product_by_id(product_id=product_id, session=session)
    return product


@router.get("/", response_model=List[GetProduct])
async def get_products(available: bool | None = True, session: SessionFactory = Depends(get_session)):
    products = await ProductService.get_products(session=session, available=available)
    return products


@router.delete("/{product_id}/hard", response_model=GetProduct)
async def delete_hard_product(product_id: int, session: SessionFactory = Depends(get_session)):
    deleted_product = await ProductService.delete_product(session=session, product_id=product_id, mode="hard")
    return deleted_product


@router.delete("/{product_id}/soft", response_model=GetProduct)
async def delete_soft_product(product_id: int, session: SessionFactory = Depends(get_session)):
    deleted_product = await ProductService.delete_product(session=session, product_id=product_id)
    return deleted_product


@router.post("/", response_model=GetProduct)
async def add_product(data: NewProduct, session: SessionFactory = Depends(get_session)):
    """
       Создание товара со все йэтой информацией:

       - **name**: каждый товар должен иметь название
       - **description**: длинное описание товара
       - **price**: обязательно
       - **stock**: количество > 0
       - **category_id**: каждый товар должен принадлежать хотя бы к одной категории
       """
    product = await ProductService.create_new_product(new_product=data, session=session)
    return product

@router.post("/{product_id}", response_model=GetProduct)
async def update_product(product_id: int, product):

    return
