from app.storage.postgresql.repositories.user_repository import UserReposetory
from app.schemas.user import NewUser, GetUser, UpdateUserName, UpdateUserEmail, GetNewUser

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> GetUser:
        try:
            user_orm = await UserReposetory.get_user_by_id(user_id, session)
            return GetUser.from_orm(user_orm)
        except ValueError as e:
            # Преобразуем внутреннюю ошибку репозитория в HTTP-ответ
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> GetNewUser:
        try:
            user_orm = await UserReposetory.get_user_by_email(user_email=email, session=session)
            return GetNewUser.from_orm(user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> GetUser:
        try:
            deleted_user_orm = await UserReposetory.delete_user_by_id(user_id, session)
            return GetUser.from_orm(deleted_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def update_user_name(data: UpdateUserName, session: AsyncSession) -> GetUser:
        try:
            updated_user_orm = await UserReposetory.update_user_name(
                user_id=data.id,
                session=session,
                first_name=data.first_name,
                last_name=data.last_name
            )
            return GetUser.from_orm(updated_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

    @staticmethod
    async def update_user_email(data: UpdateUserEmail, session: AsyncSession) -> GetUser:
        try:
            updated_user_orm = await UserReposetory.update_user_email(
                user_id=data.id,
                new_email=data.email,
                session=session
            )
            return GetUser.from_orm(updated_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )

    @staticmethod
    async def get_all_users(session: AsyncSession) -> List[GetUser]:
        users_orm = await UserReposetory.get_all_users(session)
        if not users_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Пользователей нет")
            )
        return [GetUser.from_orm(user) for user in users_orm]

    @staticmethod
    async def create_new_user(data: NewUser, session) -> GetNewUser:
        hashed_password = data.password
        try:
            new_user_orm = await UserReposetory.create_new_user(first_name=data.first_name,
                                                                last_name=data.last_name,
                                                                email=data.email,
                                                                hashed_password=hashed_password,
                                                                session=session)
            return GetNewUser.from_orm(new_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
