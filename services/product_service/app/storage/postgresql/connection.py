from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool
from typing import AsyncGenerator
import os

from app.config_ import settings


DATABASEURL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASEURL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
