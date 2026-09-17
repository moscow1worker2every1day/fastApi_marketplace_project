from contextlib import asynccontextmanager
from typing import AsyncGenerator
from redis.asyncio import Redis
from services.product_service.app.config import settings

class RedisConnection:

    _client: Redis | None = None

    @classmethod
    async def _create_connection(cls) -> None:
        if cls._client is not None:
            try:
                await cls._client.ping()
                return
            except Exception as e:
                await cls._client.aclose()
                raise e
        
        cls._client = Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            password=settings.redis.password,
            decode_responses=True,
            encoding="utf-8",
        )

    @classmethod
    async def _close_connection(cls) -> None:
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
    
    @classmethod
    def client(cls) -> Redis:
        if cls._client is None:
            raise RuntimeError("Redis connection not established")
        return cls._client

    # @asynccontextmanager
    # async def connection(cls) -> AsyncGenerator[Redis, None]:
    #     try:
    #         await cls._create_connection()
    #         yield cls._client
    #     finally:
    #         await cls._close_connection()

    @classmethod
    async def __aenter__(cls) -> Redis:
        await cls._create_connection()
        return cls._client
    
    @classmethod
    async def __aexit__(cls, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> None:
        await cls._close_connection()