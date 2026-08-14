from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.autorization import router as auth_router
from app.api.user_accounts import router as user_accounts_router
from app.api.users import router as user_router
from app.middlewares.middleware import log_requests
from app.constants import OPENAPI_DESCRIPTION, OPENAPI_TAGS
from app.config import settings
from app.log import configure_logging, startup_logger
from app.storage.postgresql.connection import DatabaseManager, SessionDep
from app.messaging.rabbitMQ.connection import RabbitMQConnectionManager
from app.messaging.rabbitMQ.consumers.consumer import start_user_service_consumer


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan for the application.
     - Checking the connection to the database and creating tables.
     - Checking the connection to the RabbitMQ and starting the consumer.
     - Starting the service.
    """
    startup_logger.info("Startup user-service")
    try:
        try:
            async with DatabaseManager.session_factory() as session:
                startup_logger.info("Checking the database connection...")
                await DatabaseManager.check_connection(session)
                await DatabaseManager.run_migrations(session)
        except Exception as e:
            startup_logger.error(
                "Connection to the database failed: "
                f"{type(e).__name__} - {e}. "
            )
            raise

    # async with DatabaseManager.session_factory() as session:
    #     try:
    #         pass
    #         #await DatabaseMarkerService.mark_database(session)
    #     except Exception as e:
    #         startup_logger.error(
    #             "Failed to mark the database: "
    #             f"{type(e).__name__} - {e}. "
    #             "Shuting down service..."
    #         )
    #         raise

        async with RabbitMQConnectionManager() as connection:
            startup_logger.info("Checking the RabbitMQ connection...")
            await connection.check_connection()
            app.state.rabbitmq_connection = connection
            startup_logger.info("RabbitMQ connection is successful")

            try:
                consumer_task = asyncio.create_task(start_user_service_consumer())
                startup_logger.info("RabbitMQ consumer started")

                startup_logger.info("Service is ready to accept requests.")
                yield
                startup_logger.info("Shuting down service...")

            except Exception as e:
                startup_logger.error(
                    "Error starting RabbitMQ consumer: "
                    f"{type(e).__name__} - {e}. "
                )
                raise

            finally:
                consumer_task.cancel()

    except Exception as e:
        startup_logger.error(
            "Startup service filed with error: "
            f"{type(e).__name__} - {e}. "
        )
        raise


app = FastAPI( 
    lifespan=lifespan,
    title="User Service",
    summary="User Service for the E-commerce platform",
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


@app.get(
    "/healthcheck",
    tags=["Technical"],
    summary="Health check",
    description="Returns service status and current application version.",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "version": "0.1.0",
                        "databaseConnection": "ok",
                        "rabbitMQConnection": "ok",
                    },
                }
            },
        },
    },)
async def healthcheck(session: SessionDep):
    """
    Check service health.
    Return the status, version, database connection, and RabbitMQ connection.
    """
    database_connection = "ok" if await DatabaseManager.check_connection(session) else "failed"
    rabbitmq_connection = "ok" if app.state.rabbitmq_connection.check_connection() else "failed"
    return {
        "status": "ok",
        "databaseConnection": database_connection,
        "rabbitMQConnection": rabbitmq_connection,
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
