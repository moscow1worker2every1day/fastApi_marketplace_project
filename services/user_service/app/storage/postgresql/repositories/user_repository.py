from typing import Optional
from uuid import UUID

from app.storage.postgresql.models.user_model import UserOrm
from app.enums import SortOrder, UserRoles, UserSortField


from app.log import users_logger
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession


_USER_SORT_COLUMNS = {
    UserSortField.created_at: UserOrm.created_at,
    UserSortField.updated_at: UserOrm.updated_at,
    UserSortField.first_name: UserOrm.first_name,
    UserSortField.last_name: UserOrm.last_name,
    UserSortField.email: UserOrm.email,
    UserSortField.id: UserOrm.id,
}


class UserRepository:

    @staticmethod
    async def create_new_user(
            first_name: str,
            last_name: str,
            email: str,
            hashed_password: str,
            role: UserRoles,
            session: AsyncSession
    ) -> UserOrm:
        try:
            new_user = UserOrm(
                first_name=first_name,
                last_name=last_name,
                email=email,
                hashed_password=hashed_password,
                role=role,
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        except IntegrityError:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            users_logger.error(f"Cannot create new user: {type(e).__name__} - {e}")
            raise

    @staticmethod
    async def delete_user_by_id(user_id: UUID, session: AsyncSession) -> bool:
        try:
            query = delete(UserOrm).where(UserOrm.id == user_id)
            await session.execute(query)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            users_logger.error(f"Cannot delete user: User with id={user_id}: {type(e).__name__} - {e}")
            raise

    @staticmethod
    async def update_user_name(
        user_id: UUID,
        session: AsyncSession,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> UserOrm:
        try:
            update_user = await UserRepository.get_user_by_id(
                session=session,
                user_id=user_id,
            )

            if first_name is not None:
                update_user.first_name = first_name
            if last_name is not None:
                update_user.last_name = last_name

            await session.commit()
            await session.refresh(update_user)
            return update_user
        except Exception as e:
            await session.rollback()
            users_logger.error(f"Cannot update user name: User with id={user_id}: {type(e).__name__} - {e}")
            raise

    @staticmethod
    async def update_user_email(
        user_id: UUID,
        new_email: str,
        session: AsyncSession,
    ) -> UserOrm:
        try:
            update_user = await UserRepository.get_user_by_id(
                session=session,
                user_id=user_id,
            )

            update_user.email = new_email
            await session.commit()
            await session.refresh(update_user)
            return update_user

        except Exception as e:
            await session.rollback()
            users_logger.error(f"Cannot update user email: User with id={user_id}: {type(e).__name__} - {e}")
            raise

    @staticmethod
    def _build_users_order_by(
        sort_by: UserSortField,
        sort_order: SortOrder,
    ) -> list:
        column = _USER_SORT_COLUMNS[sort_by]
        direction = column.asc() if sort_order == SortOrder.asc else column.desc()
        if sort_by == UserSortField.id:
            return [direction]
        return [direction, UserOrm.id.asc()]

    @staticmethod
    async def get_all_users(
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        sort_by: UserSortField,
        sort_order: SortOrder,
        user_role: UserRoles,
    ) -> list[UserOrm]:
        query = (
            select(
                UserOrm.id,
                UserOrm.first_name,
                UserOrm.last_name,
                UserOrm.email,
                UserOrm.created_at,
                UserOrm.updated_at,
            )
            .filter(UserOrm.role == user_role)
            .order_by(*UserRepository._build_users_order_by(sort_by, sort_order))
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_by_email(user_email: str, session: AsyncSession) -> UserOrm | None:
        try:
            query = select(UserOrm).where(UserOrm.email == user_email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user
        except MultipleResultsFound as e:
            users_logger.error(f"MultipleResultsFound on {user_email}: {type(e).__name__} - {e}")
            raise

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> UserOrm:
        query = select(UserOrm).where(UserOrm.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one()
        return user
