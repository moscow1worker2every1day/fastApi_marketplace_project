from typing import List

from fastapi import APIRouter, Depends

from app.services.category_service import CategoryService
from app.storage.postgresql.connection import get_session, SessionFactory
from app.schemas.category import GetCategory, NewCategory, UpdateCategory

router = APIRouter(prefix="/categories")


@router.delete("/{category_id}", response_model=GetCategory)
async def delete_category(category_id: int, session: SessionFactory = Depends(get_session)):
    deleted_category = await CategoryService.delete_category_by_id(id=category_id, session=session)
    return deleted_category


@router.post("/", response_model=GetCategory)
async def add_category(data: NewCategory, session: SessionFactory = Depends(get_session)):
    category = await CategoryService.create_new_category(name=data.name,
                                                         description=data.description,
                                                         parent_id=data.parent_id,
                                                         session=session
                                                         )
    return category


@router.put("/{category_id}/description", response_model=GetCategory)
async def update_category_description(data: UpdateCategory, session: SessionFactory = Depends(get_session)):
    category = await CategoryService.update_category_description(category_id=data.id,
                                                                 new_description=data.description,
                                                                 session=session
                                                                 )
    return category


@router.get("/{category_id}", response_model=GetCategory)
async def get_category(category_id: int, session: SessionFactory = Depends(get_session)):
    category = await CategoryService.get_category_by_id(category_id=category_id, session=session)
    return category


@router.get("/", response_model=List[GetCategory])
async def get_categories(session: SessionFactory = Depends(get_session)):
    categories = await CategoryService.get_all_categories(session=session)
    return categories
