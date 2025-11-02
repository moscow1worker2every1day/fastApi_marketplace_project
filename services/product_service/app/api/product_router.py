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
async def get_all_products(session: SessionFactory = Depends(get_session)):
    products = await ProductService.get_products(session=session)
    return products


@router.delete("/{product_id}", response_model=GetProduct)
async def delete_product(product_id: int, session: SessionFactory = Depends(get_session)):
    deleted_product = await ProductService.delete_product(session=session, product_id=product_id)
    return deleted_product


@router.post("/", response_model=GetProduct)
async def add_product(data: NewProduct, session: SessionFactory = Depends(get_session)):
    product = await ProductService.create_new_product(new_product=data, session=session)
    return product
