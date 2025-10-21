from app.storage.postgresql.models.user_model import UserOrm
from app.schemas.user import NewUser

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

class UserReposetory:

    @staticmethod
    async def create_new_user(data: NewUser, session: AsyncSession) -> int:
        try:
            new_user = UserOrm(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
            )
            session.add(new_user)
            await session.flush()
            await session.commit()
            return new_user.id
        except IntegrityError:
            raise ValueError("Пользователь с таким email уже существует")

    @staticmethod
    async def get_user_by_email(user_email: str, session: AsyncSession):
        query = select(UserOrm).where(UserOrm.email == user_email)
        try:
            result = await session.execute(query)
            user = result.scalar_one()
            return user
        except NoResultFound:
            raise ValueError(f"Пользователь с id={user_email} не найден")

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession):
        query = select(UserOrm).where(UserOrm.id == user_id)
        try:
            result = await session.execute(query)
            user = result.scalar_one()  #выбросит NoResultFound если нет
            return user
        except NoResultFound:
            raise ValueError(f"Пользователь с id={user_id} не найден")