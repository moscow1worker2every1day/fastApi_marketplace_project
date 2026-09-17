from redis.asyncio import Redis

from app.config import settings


class RedisConnection:
    _client: Redis | None = None

    @classmethod
    async def _create_connection(cls) -> None:
        if cls._client is not None:
            try:
                await cls._client.ping()
                return
            except Exception:
                await cls._client.aclose()
                cls._client = None

        cls._client = Redis(
            host=settings.redis.host,
            port=settings.redis.port,
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

    @classmethod
    async def __aenter__(cls) -> Redis:
        await cls._create_connection()
        return cls._client

    @classmethod
    async def __aexit__(
        cls,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
    ) -> None:
        await cls._close_connection()
