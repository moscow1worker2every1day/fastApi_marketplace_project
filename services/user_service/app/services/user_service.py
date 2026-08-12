from typing import TypeVar
from uuid import UUID

from app.enums import SortOrder, UserRoles, UserSortField
from app.schemas.user import GetUser, NewUser, ResponseMessage, UpdateUserEmail, UpdateUserName
from app.services.auth_service import AuthService
from app.storage.postgresql.repositories.user_repository import UserRepository
from fastapi import HTTPException, status
from app.log import users_logger
from app.storage.postgresql.models.user_model import UserOrm
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

_OrmT = TypeVar("_OrmT")


class UserService:
    """Сервис операций с пользователями."""

    @staticmethod
    def _to_get_user(orm: UserOrm) -> GetUser:
        """Преобразует ORM-модель в схему GetUser."""
        return GetUser.model_validate(orm)

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> GetUser:
        try:
            user_orm = await UserRepository.get_user_by_id(session, user_id)
            return UserService._to_get_user(user_orm)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User id={user_id} not found",
            )
        except Exception as e:
            users_logger.error(f"Cannot get user by id: User with id={user_id}: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot get user by id: User with id={user_id}: {type(e).__name__} - {e}",
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
            user_orm = await UserRepository.get_user_by_email(
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
    async def delete_user(user_id: UUID, session: AsyncSession) -> ResponseMessage:
        try:
            is_deleted = await UserRepository.delete_user_by_id(user_id, session)
            users_logger.info(f"User with id={user_id} deleted successfully")
            return ResponseMessage(
                message=f"User with id={user_id} deleted successfully: {is_deleted}",
                user_id=user_id,
            )
        except Exception as e:
            users_logger.error(f"Cannot delete user: User with id={user_id}: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot delete user: User with id={user_id}: {type(e).__name__} - {e}",
            )

    @staticmethod
    async def update_user_name(user_id: UUID, data: UpdateUserName, session: AsyncSession) -> GetUser:
        try:
            updated_user_orm = await UserRepository.update_user_name(
                user_id=user_id,
                session=session,
                first_name=data.first_name,
                last_name=data.last_name,
            )
            return UserService._to_get_user(updated_user_orm)
        except Exception as e:
            users_logger.error(f"Cannot update user name: User with id={user_id}: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot update user name: User with id={user_id}: {type(e).__name__} - {e}",
            )

    @staticmethod
    async def update_user_email(
        user_id: UUID,
        data: UpdateUserEmail, session: AsyncSession
    ) -> GetUser:
        try:
            updated_user_orm = await UserRepository.update_user_email(
                user_id=user_id, new_email=data.email, session=session
            )
            return UserService._to_get_user(updated_user_orm)
        except IntegrityError:
            users_logger.error(f"Cannot update user email: User with id={user_id}: email already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email={data.email} already exist",
            )
        except Exception as e:
            users_logger.error(f"Cannot update user email: User with id={user_id}: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot update user email: User with id={user_id}: {type(e).__name__} - {e}",
            )

    @staticmethod
    async def get_all_users(
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        sort_by: UserSortField,
        sort_order: SortOrder,
        user_role: UserRoles,
    ) -> list[GetUser]:
        users_orm = await UserRepository.get_all_users(
            session,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            user_role=user_role,
        )
        return [UserService._to_get_user(u) for u in users_orm]

    @staticmethod
    async def create_new_user(data: NewUser, session) -> GetUser:
        hashed_password = AuthService.hash_password(data.password).decode("utf-8")
        try:
            new_user_orm = await UserRepository.create_new_user(
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
        except Exception as e:
            users_logger.error(f"Cannot create new user: {type(e).__name__} - {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot create new user: {type(e).__name__} - {e}",
            )
