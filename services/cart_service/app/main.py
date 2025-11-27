from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.middlewares.middleware import catch_server_error
from app.logging import logging
from app.storage.redis.connection import RedisService, redis_connection
from app.api.cart_router import router

from app.messaging.rabbitmq.consumer import Consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logging.info(f"Startup starting...")
        await RedisService.check_redis_connection()
        yield
    except Exception as e:
        logging.error(f"Startup failed: {e}")
        raise


app = FastAPI(
    title="Cart Service",
    description="Микро-сервис корзины",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

app.middleware("http")(catch_server_error())


@app.get('/')
async def check_redis():
    await redis_connection.set("key", "value")
    value = await redis_connection.get("key")
    return {"recived_value": value}


@app.get('/rmq')
async def check_consume():
    rmq = await Consumer.consume_product_delete()
    return {"msg": "ok"}
