from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import settings
from app.log import startup_logger

class RedisService:
    _connection: Redis | None = None

    @classmethod
    async def init(cls) -> None:
        if cls._connection is None:
            try:
                cls._connection = Redis(
                    host=settings.redis.host,
                    port=settings.redis.port,
                    decode_responses=True,
                )
                startup_logger.info(
                    "Redis connection established at %s:%s",
                    settings.redis.host,
                    settings.redis.port,
                )
            except (ConnectionError, TimeoutError) as exc:
                startup_logger.error("Cannot connect to Redis: %s", exc)
                raise RedisError("Cannot connect to Redis") from exc

    @classmethod
    async def check_redis_connection(cls) -> bool:
        if cls._connection is None:
            raise RuntimeError("Redis not initialized")
        return bool(await cls._connection.ping())

    @classmethod
    def get_connection(cls) -> Redis:
        if cls._connection is None:
            raise RuntimeError("Redis not initialized")
        return cls._connection

    @classmethod
    async def close(cls) -> None:
        if cls._connection is not None:
            await cls._connection.close()
            cls._connection = None
            startup_logger.info("Redis connection closed")
