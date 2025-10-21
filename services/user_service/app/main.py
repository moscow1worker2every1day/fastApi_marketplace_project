from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import logging

from app.api.users import router as user_router
from app.storage.postgresql.connection_service import DataBaseService
from app.middlewares.logging import create_logging_middleware


logger = logging.getLogger("auth_srvice_logger")

logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

@asynccontextmanager
async def lifespan(app: FastAPI):
    dbservice = DataBaseService(logger=logger)
    try:
        await dbservice.check_connection()
        await dbservice.create_tables()
        yield
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

app = FastAPI(
    title="User Service",
    description="Микро-сервис пользователей",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(user_router)

app.middleware("http")(create_logging_middleware(logger))

