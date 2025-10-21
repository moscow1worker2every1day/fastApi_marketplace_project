from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import asyncio

from .connection import engine
from .models import Base

class DataBaseService:
    def __init__(self, logger):
        self.logger = logger
    async def check_connection(self, retries=5, delay=2):
        for i in range(retries):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    self.logger.info("Database connection successful")
                    return True
            except SQLAlchemyError:
                self.logger.warning(f"Waiting for DB... retry {i + 1}/{retries}")
                await asyncio.sleep(delay)
        raise Exception("Could not connect to database")

    async def create_tables(self):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
