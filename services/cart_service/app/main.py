import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.cart_router import router
from app.config import settings
from app.logging import log
from app.messaging.rabbitmq.connection import RabbitMQConnectionManager
from app.messaging.rabbitmq.consumer import start_product_events_consumer
from app.middlewares.middleware import catch_server_error
from app.storage.redis.connection import RedisService


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task: asyncio.Task | None = None

    try:
        log.info("Startup cart-service")
        await RedisService.init()
        await RedisService.check_redis_connection()
        log.info("Redis connection is successful")

        async with RabbitMQConnectionManager() as connection:
            await connection.check_connection()
            app.state.rabbitmq_connection = connection
            log.info("RabbitMQ connection is successful")

            consumer_task = asyncio.create_task(start_product_events_consumer())
            log.info("RabbitMQ consumer started")
            log.info("Service is ready to accept requests.")
            yield
            log.info("Shutting down cart-service...")
    except Exception as e:
        log.exception("Startup failed: %s", e)
        raise
    finally:
        if consumer_task is not None:
            consumer_task.cancel()
        await RedisService.close()


app = FastAPI(
    title="Cart Service",
    description="Cart Service",
    version=settings.app.version,
    lifespan=lifespan,
)

app.include_router(router)
app.middleware("http")(catch_server_error())


@app.get(
    "/healthcheck",
    tags=["Technical"],
    summary="Health check",
)
async def healthcheck():
    redis_ok = False
    rabbit_ok = False
    try:
        redis_ok = await RedisService.check_redis_connection()
    except Exception:
        redis_ok = False
    try:
        await app.state.rabbitmq_connection.check_connection()
        rabbit_ok = True
    except Exception:
        rabbit_ok = False

    return {
        "status": "ok" if redis_ok and rabbit_ok else "degraded",
        "redisConnection": "ok" if redis_ok else "failed",
        "rabbitMQConnection": "ok" if rabbit_ok else "failed",
        "version": settings.app.version,
    }
