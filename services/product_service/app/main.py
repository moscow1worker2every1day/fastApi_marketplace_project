from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.middlewares.middleware import error_handler_middleware
from app.storage.postgresql.connection_service import DataBaseService
from app.logging import logging
from app.api.category_router import router as category_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await DataBaseService.check_connection(logging)
        await DataBaseService.create_tables(logging)
        yield
    except Exception as e:
        logging.error(f"Startup failed: {e}")
        raise

app = FastAPI(
    title="Product Service",
    description="Микро-сервис товаров",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(category_router)

app.middleware("http")(error_handler_middleware())


@app.get("/")
async def check():
    res = await DataBaseService.check_connection(logging)
    return {"msg": f"{res}"}
