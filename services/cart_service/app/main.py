from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.middlewares.middleware import catch_server_error
from app.logging import log
from app.storage.redis.connection import RedisService
from app.api.cart_router import router

from app.messaging.rabbitmq.consumer import Consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        log.info(f"Startup starting...")
        await RedisService.init()
        await RedisService.check_redis_connection()
        '''
        отдельный процесс для получения сообщений
        consumer_task = asyncio.create_task(
            Consumer.consume_product_delete()
        )
        '''
        yield
    except Exception as e:
        log.exception(f"Startup failed: {e}")
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
    await RedisService.get_connection().set("key", "value")
    value = await RedisService.get_connection().get("key")
    return {"recived_value": value}

@app.get('/redis_connection')
async def get_redis():
    return {"recived_value": dict(RedisService.get_connection())}

'''
@app.get('/rmq')
async def check_consume():
    rmq = await Consumer.consume_product_delete()
    return {"msg": "ok"}
'''