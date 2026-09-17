import asyncio
import sys
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.config import settings
from app.log import startup_logger


def _import_alembic():
    """Import real alembic package, avoiding shadow by local alembic/ folder."""
    service_root = str(Path(__file__).resolve().parents[3])
    removed: list[str] = []
    for path in (service_root, "", str(Path.cwd())):
        while path in sys.path:
            sys.path.remove(path)
            removed.append(path)
    try:
        from alembic import command
        from alembic.config import Config
    finally:
        for path in reversed(removed):
            sys.path.insert(0, path)
    return command, Config


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
        """Creates an asynchronous session for working with the database."""
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
                startup_logger.info("Connected to the database successfully")
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
    async def run_migrations(session: AsyncSession) -> None:
        """Runs migrations, then ensures ORM tables exist."""
        try:
            command, Config = _import_alembic()
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
            startup_logger.warning(
                f"Migrations failed: {type(e).__name__} - {e}. "
                "Attempting to create tables directly."
            )
            raise e


SessionDep = Annotated[AsyncSession, Depends(DatabaseManager.get_session)]
