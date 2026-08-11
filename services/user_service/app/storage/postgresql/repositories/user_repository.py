import logging
from typing import Optional
from uuid import UUID

from app.storage.postgresql.models.user_model import UserOrm
from app.enums import UserRoles


from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

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
            logger.error(f"Cannot create new user: {type(e).__name__} - {e}")
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
            logger.error(f"Cannot delete user: User with id={user_id}: {type(e).__name__} - {e}")
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
            logger.error(f"Cannot update user name: User with id={user_id}: {type(e).__name__} - {e}")
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
            logger.error(f"Cannot update user email: User with id={user_id}: {type(e).__name__} - {e}")
            raise

    @staticmethod
    async def get_all_users(session: AsyncSession) -> list[UserOrm]:
        query = select(UserOrm)
        result = await session.execute(query)
        users = result.scalars().all()
        return [user for user in users]

    @staticmethod
    async def get_user_by_email(user_email: str, session: AsyncSession) -> UserOrm | None:
        try:
            query = select(UserOrm).where(UserOrm.email == user_email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user
        except MultipleResultsFound as e:
            logger.error(f"MultipleResultsFound on {user_email}: {type(e).__name__} - {e}")
            raise

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> UserOrm:
        query = select(UserOrm).where(UserOrm.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one()
        return user
