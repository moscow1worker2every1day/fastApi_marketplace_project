import os

from dotenv import load_dotenv
from redis.asyncio import Redis

from app.logging import logging

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

redis_connection = Redis(host="redis", port=6379,  encoding="utf-8", decode_responses=True)


class RedisService:

    @staticmethod
    async def check_redis_connection() -> Redis:
        pong = await redis_connection.ping()
        logging.info(f"Redis check connetion: {pong}")
        return redis_connection

    @staticmethod
    async def close() -> True:
        global redis_connection
        if redis_connection:
            await redis_connection.close()
            redis_connection = None
        return True

    @staticmethod
    async def get_cart_key(user_id: int) -> str:
        return f"cart:{user_id}"
