from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.messaging.rabbitMQ.connection import get_rabbit_connection
from app.middlewares.middleware import error_handler_middleware
from app.storage.postgresql.connection_service import DataBaseService
from app.logging import log

from app.api.category_router import router as category_router
from app.api.product_router import router as product_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await DataBaseService.check_connection(log)
        await DataBaseService.create_tables(log)
        yield
        log.info("PRODUCT SERVICE STOPPED")
    except Exception as e:
        log.error(f"Startup failed: {e}")
        raise

app = FastAPI(
    title="Product Service",
    description="Микро-сервис товаров",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(category_router)
app.include_router(product_router)

app.middleware("http")(error_handler_middleware())


@app.get("/")
async def check():
    res = await DataBaseService.check_connection(log)
    return {"msg": f"{res}"}


@app.get("/rmq")
async def check_rmq():
    with get_rabbit_connection() as connection:
        print("RabbitMQ connection OK!")
        with connection.channel() as channel:
            print("RabbitMQ connection to channel OK!")


    return {"msg": "ok"}
