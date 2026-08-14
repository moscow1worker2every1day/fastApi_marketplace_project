import asyncio
from typing import Annotated

from fastapi import Depends
from app.log import startup_logger
from app.storage.postgresql.models.base_model import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

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
        """
        async with cls.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @staticmethod
    async def check_connection(session: AsyncSession, retries: int = 10, delay: int = 1) -> bool:
        """Checking the connection to the database."""
        for i in range(retries):
            try:
                await session.execute(text("SELECT 1"))
                startup_logger.info(f"Connected to the database successfully")
                return True
            except Exception as e:
                if i == retries - 1:
                    raise Exception(
                        f"Could not connect to database after {retries} retries: "
                        f"{type(e).__name__} - {e}"
                    )
                startup_logger.error(
                    f"Could not connect to database after {i+1} retries: "
                    f"{type(e).__name__} - {e}"
                )
                await asyncio.sleep(delay)

    @staticmethod
    async def create_tables() -> None:
        """Creating tables in the database from SQLAlchemy metadata."""
        try:
            async with DatabaseManager.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            startup_logger.error(
                "Failed to database create tables: "
                f"{type(e).__name__} - {e}"
            )
            raise


SessionDep = Annotated[AsyncSession, Depends(DatabaseManager.get_session)]
