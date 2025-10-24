from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.api.users import router as user_router
from app.storage.postgresql.connection_service import DataBaseService
from app.middlewares.logging import create_logging_middleware


logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await DataBaseService.check_connection(logging=logging)
        await DataBaseService.create_tables(logging=logging)
        yield
    except Exception as e:
        logging.error(f"Startup failed: {e}")
        raise

app = FastAPI(
    title="User Service",
    description="Микро-сервис пользователей",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_router)

app.middleware("http")(create_logging_middleware(logger))

