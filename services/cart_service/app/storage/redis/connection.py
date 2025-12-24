import os

from dotenv import load_dotenv
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.logging import log

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST_TEST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

redis_connection: Redis | None = None  # глобальная переменная для singleton


class RedisService:

    @classmethod
    async def init(cls):
        global redis_connection
        if redis_connection is None:
            try:
                redis_connection = Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    decode_responses=True
                )
                log.info("Redis connection established")
            except (ConnectionError, TimeoutError) as exc:
                log.exception("Cannot connect to Redis")
                raise RedisError

    @staticmethod
    async def check_redis_connection() -> Redis:
        """Проверка подключения Redis"""
        if redis_connection is None:
            raise RuntimeError("Redis not initialized")
        pong = await redis_connection.ping()

        return redis_connection

    @classmethod
    def get_connection(cls) -> Redis:
        """Получить экземпляр Redis"""
        if redis_connection is None:
            raise RuntimeError("Redis not initialized")
        return redis_connection

    @classmethod
    async def close(cls):
        """Закрыть соединение Redis при shutdown"""
        global redis_connection
        if redis_connection:
            await redis_connection.close()
            redis_connection = None
            log.info("Redis connection closed")
