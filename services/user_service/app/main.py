from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import logging
from sqlalchemy import text

from app.storage.postgresql.connection import get_session, SessionFactory
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

#app.include_router(user_router)

app.middleware("http")(create_logging_middleware(logger))

@app.get("/")
async def test_db(session: SessionFactory = Depends(get_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {"messsage": "success"}
    except:
        return {"messsage": "not success"}
