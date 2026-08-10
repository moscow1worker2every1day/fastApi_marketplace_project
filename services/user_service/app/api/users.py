from typing import Annotated

from app.dependencies.auth_user_dependency import (get_current_active_user,
                                                   get_current_user_role)
from app.dependencies.user_service_dependency import UserServiceDep
from app.schemas.user import GetUser, NewUser, UpdateUserEmail, UpdateUserName
from app.storage.postgresql.connection import SessionFactory, get_session
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users")

SessionDep = Annotated[SessionFactory, Depends(get_session)]


@router.get("/my_account/", response_model=GetUser, tags=["User Account"])
async def get_user_account(
    current_user: Annotated[GetUser, Depends(get_current_active_user)],
):
    return current_user


@router.get("/{user_id}", response_model=GetUser, tags=["CRUD"])
async def get_user(
    user_id: int,
    session: SessionDep,
    user_service: UserServiceDep,
    current_user: Annotated[GetUser, Depends(get_current_active_user)],
):
    """
    если нужно чтобы пользователь мог искать только самого себя
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    """
    user = await user_service.get_user_by_id(user_id=user_id, session=session)
    return user


@router.get("/", response_model=list[GetUser], tags=["CRUD"])
async def get_all_users(
    session: SessionDep,
    user_service: UserServiceDep,
    current_user: Annotated[GetUser, Depends(get_current_user_role)],
):
    users = await user_service.get_all_users(session=session)
    return users


@router.post(
    "/", response_model=GetUser, status_code=status.HTTP_201_CREATED, tags=["CRUD"]
)
async def add_user(data: NewUser, session: SessionDep, user_service: UserServiceDep):
    user = await user_service.create_new_user(data=data, session=session)
    return user


@router.delete("/{user_id}", response_model=GetUser, tags=["CRUD"])
async def delete_user(
    user_id: int,
    session: SessionDep,
    user_service: UserServiceDep,
    current_user: Annotated[GetUser, Depends(get_current_active_user)],
):
    user = await user_service.delete_user(user_id=user_id, session=session)
    return user


@router.put("/{user_id}/name", response_model=GetUser, tags=["CRUD"])
async def update_user_name(
    data: UpdateUserName,
    session: SessionDep,
    user_service: UserServiceDep,
    current_user: Annotated[GetUser, Depends(get_current_active_user)],
):
    updated_user = await user_service.update_user_name(data=data, session=session)
    return updated_user


@router.put("/{user_id}/email", response_model=GetUser, tags=["CRUD"])
async def update_user_email(
    data: UpdateUserEmail,
    session: SessionDep,
    user_service: UserServiceDep,
    current_user: Annotated[GetUser, Depends(get_current_active_user)],
):
    updated_user = await user_service.update_user_email(data=data, session=session)
    return updated_user
