from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from alembic.config import Config
from alembic import command
import asyncio

from app.storage.postgresql.models import Base
from app.storage.postgresql.connection import DatabaseManager
from app.config import settings
from app.log import startup_logger


class DataBaseService:
    @staticmethod
    async def check_connection(session: AsyncSession, retries: int = 10, delay: int = 1) -> None:
        """
        Checking the connection to the database.
        """
        for i in range(retries):
            try:
                await session.execute(text("SELECT 1"))
                return
            except Exception as e:
                if i == retries - 1:
                    raise Exception(
                        f"Could not connect to database after {retries} retries: "
                        f"{type(e).__name__} - {e}"
                    )
                await asyncio.sleep(delay)

    @staticmethod
    async def _create_tables_directly() -> None:
        """
        Creating tables in the database from SQLAlchemy metadata.
        Safe to call repeatedly: only missing tables/types are created.
        """
        try:
            async with DatabaseManager.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            startup_logger.info(
                "Tables created/verified using SQLAlchemy metadata."
            )
        except Exception as e:
            startup_logger.error(
                "Failed to database create tables: "
                f"{type(e).__name__} - {e}"
            )
            raise

    @staticmethod
    async def run_migrations(session: AsyncSession) -> None:
        """Runs migrations, then ensures ORM tables exist."""
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
            startup_logger.warning(
                f"Migrations failed: {type(e).__name__} - {e}. "
                "Attempting to create tables directly."
            )

        # Alembic may succeed with an empty versions/ folder and create nothing.
        await DataBaseService._create_tables_directly()
