from typing import List, Optional

from fastapi import APIRouter, Depends
from app.schemas.user import NewUser, GetUser, UpdateName
from app.services.user_service import UserService
from app.storage.postgresql.connection import get_session, SessionFactory

router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=GetUser | dict)
async def get_user(user_id: int, session: SessionFactory = Depends(get_session)):
    user = await UserService.get_user_by_id(user_id, session)
    return GetUser.model_validate(user)


@router.get("/", response_model=List[GetUser])
async def get_all_users(session: SessionFactory = Depends(get_session)):
    users = await UserService.get_all_users(session)
    return users


@router.post("/", response_model=GetUser)
async def add_user(data: NewUser, session: SessionFactory = Depends(get_session)):
    user = await UserService.create_new_user(data, session)
    return user

@router.delete("/{iser_id}", response_model=GetUser)
async def delete_user(user_id: int, session: SessionFactory = Depends(get_session)):
    user = await UserService.delete_user(user_id=user_id, session=session)
    return user

@router.put("/{iser_id}", response_model=GetUser)
async def update_user_name(data: UpdateName, session: SessionFactory = Depends(get_session)):
    #доделать схему
    user = await UserService.update_user_name(user_id=data.id, session=session)
    return user
#доделать update email