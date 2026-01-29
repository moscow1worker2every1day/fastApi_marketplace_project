from typing import Annotated

from fastapi import APIRouter, Depends, status
from app.schemas.user import NewUser, GetUser, UpdateUserName, UpdateUserEmail
from app.services.user_service import UserService
from app.storage.postgresql.connection import get_session, SessionFactory

from app.dependencies.auth_user_dependency import get_current_active_user, get_current_user_role

router = APIRouter(prefix="/users")

SessionDep = Annotated[SessionFactory, Depends(get_session)]


@router.get("/my_account/", response_model=GetUser, tags=["User Account"])
async def get_user_account(
        current_user: Annotated[GetUser, Depends(get_current_active_user)]
):
    return current_user


@router.get("/{user_id}", response_model=GetUser, tags=["CRUD"])
async def get_user(
    user_id: int, 
    session: SessionDep, 
    current_user: Annotated[GetUser, Depends(get_current_active_user)]
):
    '''
    если нужно чтобы пользователя мог искать только самого себя
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    '''
    user = await UserService.get_user_by_id(user_id=user_id, session=session)
    return user


@router.get("/", response_model=list[GetUser], tags=["CRUD"])
async def get_all_users(
    session: SessionDep, 
    current_user: Annotated[GetUser, Depends(get_current_user_role)]
):
    users = await UserService.get_all_users(session=session)
    return users


@router.post("/", response_model=GetUser, status_code=status.HTTP_201_CREATED, tags=["CRUD"])
async def add_user(data: NewUser, session: SessionDep):
    user = await UserService.create_new_user(data=data, session=session)
    return user


@router.delete("/{user_id}", response_model=GetUser, tags=["CRUD"])
async def delete_user(
    user_id: int, 
    session: SessionDep, 
    current_user: Annotated[GetUser, Depends(get_current_active_user)]
):
    user = await UserService.delete_user(user_id=user_id, session=session)
    return user


@router.put("/{user_id}/name", response_model=GetUser, tags=["CRUD"])
async def update_user_name(
    data: UpdateUserName, 
    session: SessionDep, 
    current_user: Annotated[GetUser, Depends(get_current_active_user)]
):
    updated_user = await UserService.update_user_name(data=data, session=session)
    return updated_user


@router.put("/{user_id}/email", response_model=GetUser, tags=["CRUD"])
async def update_user_email(
    data: UpdateUserEmail, 
    session: SessionDep,  
    current_user: Annotated[GetUser, Depends(get_current_active_user)]
):
    updated_user = await UserService.update_user_email(data=data, session=session)
    return updated_user


