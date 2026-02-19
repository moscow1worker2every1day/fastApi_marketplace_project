from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool
from typing import AsyncGenerator

from app.config import settings

print(settings.DB_URL)

engine = create_async_engine(
    settings.DB_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
