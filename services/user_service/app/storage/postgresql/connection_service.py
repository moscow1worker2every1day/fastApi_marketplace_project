from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from alembic import command
from loguru import logger
import asyncio

from app.storage.postgresql.connection import engine
from app.storage.postgresql.models import Base
from app.config import settings
from app.log import startup_logger


class DataBaseService:
    @staticmethod
    async def check_connection(retries: int = 10, delay: int = 1) -> None:
        """
        Checking the connection to the database.
        """
        for i in range(retries):
            try:
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
                    return
            except Exception as e:
                if i == retries - 1:
                    raise Exception(
                        f"Could not connect to database after {retries} retries: "
                        f"{type(e).__name__} - {e}"
                    )
                await asyncio.sleep(delay)

    @staticmethod
    async def _create_tables_directly(connection: AsyncSession):
        """
        Creating tables in the database.
        """
        try:
            Base.metadata.create_all(bind=connection.engine)
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
    def run_migrations(connection: AsyncSession):
        """Runs migrations if the database is not on the latest version."""
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
            script_dir = ScriptDirectory.from_config(alembic_cfg)
            migration_context = MigrationContext.configure(connection)

            current_db_revision = migration_context.get_current_revision()
            head_revision = script_dir.get_current_head()

            if current_db_revision != head_revision:
                startup_logger.info(
                    f"Running migrations: "
                    f"current={current_db_revision}, "
                    f"head={head_revision}"
                )
                command.upgrade(alembic_cfg, "head")
                startup_logger.info(
                    "Migrations completed successfully."
                )
            else:
                logger.bind(route_group=settings.loguru.startup_log_name).info(
                    "Database is up to date, no migrations needed."
                )
        except Exception as e:
            logger.bind(route_group=settings.loguru.startup_log_name).warning(
                f"Migrations failed: {type(e).__name__} - {e}. "
                "Attempting to create tables directly."
            )
        
        try:
            DataBaseService._create_tables_directly(connection)
        except Exception:
            raise
