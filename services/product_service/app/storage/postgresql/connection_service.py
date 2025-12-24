import asyncio

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.storage.postgresql.connection import engine
from app.storage.postgresql.models.base_model import Base


class DataBaseService:
    @staticmethod
    async def check_connection(log=None, retries=0, delay=0) -> bool:
        for i in range(retries):
            try:
                async with engine.connect() as conn:
                    res = await conn.execute(text("SELECT 1"))
                    if log:
                        log.info(f"Database connection successful: {res}")
                    return True
            except SQLAlchemyError:
                if log:
                    log.warning(f"Waiting for DB... retry {i + 1}/{retries}")
                await asyncio.sleep(delay)
        raise Exception("Could not connect to database")

    @staticmethod
    async def create_tables(log=None) -> bool:
        async with engine.begin() as connection:
            try:
                res = await connection.run_sync(Base.metadata.create_all)
                if log:
                    log.info(f"Created database tables {res}")
                return True
            except Exception as e:
                if log:
                    log.warning(f"Error create database tables {e}")
                return False
