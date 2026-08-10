from typing import List, TypeVar

from app.schemas.user import GetUser, NewUser, UpdateUserEmail, UpdateUserName
from app.services.auth_service import AuthService
from app.storage.postgresql.repositories.user_repository import UserReposetory
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

_OrmT = TypeVar("_OrmT")


class UserService:
    """Сервис операций с пользователями."""

    @staticmethod
    def _to_get_user(orm: _OrmT) -> GetUser:
        """Преобразует ORM-модель в схему GetUser."""
        return GetUser.model_validate(orm)

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> GetUser:
        try:
            user_orm = await UserReposetory.get_user_by_id(user_id, session)
            return UserService._to_get_user(user_orm)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User id={user_id} not found",
            )

    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession) -> GetUser:
        """
        Validate if email exist in db and get information
        :param email: str
        :param session: session database
        :return: user: GetUser
        """
        try:
            user_orm = await UserReposetory.get_user_by_email(
                user_email=email, session=session
            )
        except MultipleResultsFound:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Incorrect data"
            )
        if user_orm is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not find user with email '{email}'",
            )
        return UserService._to_get_user(user_orm)

    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> GetUser:
        try:
            deleted_user_orm = await UserReposetory.delete_user_by_id(user_id, session)
            return UserService._to_get_user(deleted_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @staticmethod
    async def update_user_name(data: UpdateUserName, session: AsyncSession) -> GetUser:
        try:
            updated_user_orm = await UserReposetory.update_user_name(
                user_id=data.id,
                session=session,
                first_name=data.first_name,
                last_name=data.last_name,
            )
            return UserService._to_get_user(updated_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )

    @staticmethod
    async def update_user_email(
        data: UpdateUserEmail, session: AsyncSession
    ) -> GetUser:
        try:
            updated_user_orm = await UserReposetory.update_user_email(
                user_id=data.id, new_email=data.email, session=session
            )
            return UserService._to_get_user(updated_user_orm)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @staticmethod
    async def get_all_users(session: AsyncSession) -> List[GetUser]:
        users_orm = await UserReposetory.get_all_users(session)
        if not users_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователей нет"
            )
        return [UserService._to_get_user(u) for u in users_orm]

    @staticmethod
    async def create_new_user(data: NewUser, session) -> GetUser:
        hashed_password = AuthService.hash_password(
            data.password).decode("utf-8")
        try:
            new_user_orm = await UserReposetory.create_new_user(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                hashed_password=hashed_password,
                role=data.role,
                session=session,
            )
            return UserService._to_get_user(new_user_orm)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Could not create user, email={data.email} already exist",
            )
