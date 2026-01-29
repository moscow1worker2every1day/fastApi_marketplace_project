import logging
from typing import Optional

from app.storage.postgresql.models.user_model import UserOrm
from app.config import UserRoles


from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class UserReposetory:

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
            await session.flush()  # занести изм в бд предварительно и получить id
            await session.commit()

            return new_user
        except IntegrityError:
            raise
        except Exception as e:
            logger.warning(f"Unknown error {e}")

    @staticmethod
    async def delete_user_by_id(user_id: int, session: AsyncSession) -> UserOrm:
        try:
            delete_user = await UserReposetory.get_user_by_id(user_id=user_id, session=session)
            await session.delete(delete_user)
            await session.commit()
            return delete_user
        except ValueError:
            raise ValueError(f"Невозможно удалить данные! Пользователь с id={user_id} не найден")

    @staticmethod
    async def update_user_name(user_id: int,
                               session: AsyncSession,
                               first_name: Optional[str] = None,
                               last_name: Optional[str] = None
                               ) -> UserOrm:
        try:
            update_user = await UserReposetory.get_user_by_id(user_id=user_id, session=session)

            if first_name is not None:
                update_user.first_name = first_name
            if last_name is not None:
                update_user.last_name = last_name

            await session.commit()
            await session.refresh(update_user)
            return update_user

        except ValueError:
            raise ValueError(f"Невозможно обновить данные! Пользователь с id={user_id} не найден")

    @staticmethod
    async def update_user_email(user_id: int,
                                new_email: str,
                                session: AsyncSession
                                ) -> UserOrm:
        try:
            update_user = await UserReposetory.get_user_by_id(user_id=user_id, session=session)

            update_user.email = new_email
            await session.commit()
            await session.refresh(update_user)
            return update_user

        except IntegrityError:
            raise ValueError(f"Невозможно обновить email! Пользователь с email={new_email} уже существует")
        except ValueError as e:
            raise ValueError(f"Невозможно обновить email! {e}")

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
            logger.warning(f"MultipleResultsFound on {user_email}: {e}")
            raise

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> UserOrm:
        query = select(UserOrm).where(UserOrm.id == user_id)
        try:
            result = await session.execute(query)
            user = result.scalar_one()  # выбросит NoResultFound если нет
            return user
        except NoResultFound:
            raise
