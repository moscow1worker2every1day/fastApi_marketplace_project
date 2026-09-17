from functools import wraps
import json
from typing import Callable

from app.storage.redis.connection import RedisConnection
from app.config import settings


def redis_cache(
    *,
    key_prefix: str,
    ttl: int = settings.redis.default_ttl,
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                redis = RedisConnection.client()
                key = f"{key_prefix}:{args[0]}"
                value = await redis.get(key)
                if value:
                    return json.loads(value)
                result = await func(*args, **kwargs)
                await redis.set(key, json.dumps(result), ex=ttl)
                return result
            except Exception as e:
                return await func(*args, **kwargs)

        return wrapper
    return decorator