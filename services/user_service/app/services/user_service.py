from app.storage.postgresql.repositories.user_repository import UserReposetory
from app.schemas.user import NewUser, GetUser

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    @staticmethod
    async def get_user_by_id(id: int, session: AsyncSession):
        try:
            user = await UserReposetory.get_user_by_id(user_id=id, session=session)
            return user
        except IntegrityError:
            raise ValueError("Пользователь с таким email уже существует")

    @staticmethod
    async def create_new_user(data: NewUser, session):
        try:
            new_user = await UserReposetory.create_new_user(data=data, session=session)
            return new_user
        except IntegrityError:
            # Если уникальное ограничение нарушено
            raise ValueError("Пользователь с таким email уже существует")
