from contextlib import asynccontextmanager

from app.api.autorization import router as auth_router
from app.api.user_accounts import router as user_accounts_router
from app.api.users import router as user_router
from app.middlewares.middleware import log_requests
from app.storage.postgresql.connection_service import DataBaseService
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.constants import OPENAPI_DESCRIPTION, OPENAPI_TAGS
from app.config import settings
from app.log import configure_logging, startup_logger
from app.storage.postgresql.connection import DatabaseManager


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan for the application.
    Checking the connection to the database and creating tables.
    """
    startup_logger.info("Startup user-service")
    try:
        async with DatabaseManager.session_factory() as session:
            startup_logger.info("Checking the database connection...")
            await DataBaseService.check_connection(session)
            await DataBaseService.run_migrations(session)
    except Exception as e:
        startup_logger.error(
            "Connection to the database failed: "
            f"{type(e).__name__} - {e}. "
            "Shuting down service..."
        )
        raise

    async with DatabaseManager.session_factory() as session:
        try:
            pass
            #await DatabaseMarkerService.mark_database(session)
        except Exception as e:
            startup_logger.error(
                "Failed to mark the database: "
                f"{type(e).__name__} - {e}. "
                "Shuting down service..."
            )
            raise

    startup_logger.info("Service is ready to accept requests.")

    yield

    startup_logger.info("Shuting down service...")


app = FastAPI( 
    lifespan=lifespan,
    title="User Service",
    description=OPENAPI_DESCRIPTION,
    version=settings.app.version,
    openapi_tags=OPENAPI_TAGS,
)

app.include_router(user_router)
app.include_router(user_accounts_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_requests)

# app.add_exception_handler(
#     RequestValidationError,
#     validation_exception_handler,
# )
# app.add_exception_handler(
#     HTTPException,
#     custom_http_exception_handler,
# )
# app.add_exception_handler(
#     Exception,
#     unhandled_exception_handler,
# )


@app.get("/healthcheck", tags=["Technical"])
async def healthcheck():
    """
    Check service health.
    Return the status, version.
    """
    return {
        "status": "ok",
        "version": settings.app.version,
    }


# if __name__ == "__main__":
#     uvicorn.run("main:app", access_log=False, **settings.app.model_dump())


# @app.get("/db", response_class=JSONResponse)
# async def check_connection(response: Response):
#     try:
#         res = await DataBaseService.check_connection(log=logging, retries=10, delay=2)
#         return {"msg": f"{res}"}
#     except Exception as e:
#         return {"msg": f"{e}"}


# @app.get("/rabbitMQ")
# async def receive_msg_from_user_service():
#     res = await get_category_msq()
#     return {"msg": f"{res}"}
