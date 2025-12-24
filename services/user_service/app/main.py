import logging

from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from contextlib import asynccontextmanager

from app.api.users import router as user_router
from app.api.autorization import router as auth_router
from app.storage.postgresql.connection_service import DataBaseService
from app.middlewares.logging import create_logging_middleware
from app.messaging.rabbitMQ.consumer import get_category_msq


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await DataBaseService.check_connection(log=logger, retries=10, delay=2)
        await DataBaseService.create_tables(log=logger)
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
app.include_router(auth_router)

app.middleware("http")(create_logging_middleware(logging))


@app.get("/db", response_class=JSONResponse)
async def check_connection(response: Response):
    try:
        res = await DataBaseService.check_connection(log=logging, retries=10, delay=2)
        return {"msg": f"{res}"}
    except Exception as e:
        return {"msg": f"{e}"}


@app.get("/rabbitMQ")
async def receive_msg_from_user_service():
    res = await get_category_msq()
    return {"msg": f"{res}"}
