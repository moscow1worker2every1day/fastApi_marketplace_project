from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import asyncio

from .connection import engine
from .models import Base

class DataBaseService:
    @staticmethod
    async def check_connection(logging, retries=2, delay=2):
        for i in range(retries):
            try:
                async with engine.connect() as conn:
                    res = await conn.execute(text("SELECT 1"))
                    logging.info(f"Database connection successful: {res}")
                    return True
            except SQLAlchemyError:
                logging.warning(f"Waiting for DB... retry {i + 1}/{retries}")
                await asyncio.sleep(delay)
        raise Exception("Could not connect to database")

    @staticmethod
    async def create_tables(logging):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            logging.info("Created database tables")
