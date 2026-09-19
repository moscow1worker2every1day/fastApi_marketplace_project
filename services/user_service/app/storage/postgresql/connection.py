from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool
from fastapi import Depends
from typing import Annotated
from sqlalchemy import text
import asyncio
from alembic.config import Config
from alembic import command

from app.log import startup_logger
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

    @staticmethod
    async def check_connection(session: AsyncSession, retries: int = 10, delay: int = 1) -> bool:
        """
        Checking the connection to the database.
        Returns:
            bool: True if connection is successful, False otherwise.
        """
        for i in range(retries):
            try:
                await session.execute(text("SELECT 1"))
                return True
            except Exception as e:
                if i == retries - 1:
                    raise Exception(
                        f"Could not connect to database after {retries} retries: "
                        f"{type(e).__name__} - {e}"
                    )
                await asyncio.sleep(delay)

    @staticmethod
    async def run_migrations(session: AsyncSession) -> None:
        """Applies Alembic migrations up to head."""
        try:
            alembic_cfg = Config(settings.alembic.alembic_ini_path)
            alembic_cfg.set_main_option(
                "script_location",
                settings.alembic.alembic_path,
            )
            alembic_cfg.set_main_option(
                "sqlalchemy.url",
                settings.postgres.sync_database_url,
            )
            command.upgrade(alembic_cfg, "head")
            startup_logger.info("Migrations completed successfully.")
        except Exception as e:
            startup_logger.error(
                f"Migrations failed: {type(e).__name__} - {e}."
            )
            raise

SessionDep = Annotated[AsyncSession, Depends(DatabaseManager.get_session)]
