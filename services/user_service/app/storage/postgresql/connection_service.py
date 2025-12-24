from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import asyncio

from app.storage.postgresql.connection import engine
from app.storage.postgresql.models import Base


class DataBaseService:
    @staticmethod
    async def check_connection(*, log=None, retries=0, delay=0):
        for i in range(retries):
            try:
                async with engine.connect() as conn: # connect требует явного коммита, а нам тут не нужно коммитить
                    res = await conn.execute(text("SELECT 1"))
                    if log:
                        log.info(f"Database connection successful: {res}")
                    return True
            except SQLAlchemyError:
                if log:
                    print(f"Waiting for DB... retry {i + 1}/{retries}")
                    log.warning(f"Waiting for DB... retry {i + 1}/{retries}")
                await asyncio.sleep(delay)
        raise Exception("Could not connect to database")

    @staticmethod
    async def create_tables(*, log=None):
        async with engine.begin() as connection: # делает сам коммит
            #await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
            if log:
                log.info("Created database tables")
