from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool
from fastapi import Depends
from typing import Annotated

from app.config import settings


class DatabaseManager:
    engine = create_async_engine(
        settings.postgres.database_url,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    @classmethod
    async def get_session(cls):
        """
        Creates an asynchronous session for working with the database.
        The session allows you to automatically manage transactions.

        Returns:
            AsyncSession: Asynchronous session for working with the database.
        Raises:
            Exception: If an error occurs while creating the session.
        """
        async with cls.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


session_dep = Annotated[AsyncSession, Depends(DatabaseManager.get_session)]
