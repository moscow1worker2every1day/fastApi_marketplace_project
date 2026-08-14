from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.category_router import router as category_router
from app.api.product_router import router as product_router
from app.config import settings
from app.constants import OPENAPI_DESCRIPTION, OPENAPI_TAGS
from app.log import configure_logging, startup_logger
from app.middlewares.middleware import log_requests
from app.storage.postgresql.connection import DatabaseManager, SessionDep
from app.messaging.rabbitMQ.connection import RabbitMQConnectionManager


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan for the application.
    Checking the connection to the database and creating tables.
    """
    startup_logger.info("Startup product-service")
    try:
        async with DatabaseManager.session_factory() as session:
            startup_logger.info("Checking the connection to the database...")
            await DatabaseManager.check_connection(session)
            startup_logger.info("Creating tables in the database...")
            await DatabaseManager.create_tables()
    except Exception as e:
        startup_logger.error(
            "Connection to the database failed: "
            f"{type(e).__name__} - {e}. "
            "Shuting down service..."
        )
        raise

    try:
        async with RabbitMQConnectionManager() as rabbit_manager:
            startup_logger.info("Checking the connection to the RabbitMQ...")
            await rabbit_manager.check_connection()
            app.state.rabbitmq_connection = rabbit_manager
            startup_logger.info("Connected to RabbitMQ")

            startup_logger.info("Service is ready to accept requests.")
            yield
            startup_logger.info("Shuting down service...")

    except Exception as e:
        startup_logger.error(
            f"Could not connect to RabbitMQ: {type(e).__name__} - {e}. "
            "Shuting down service..."
        )
        raise


app = FastAPI(
    lifespan=lifespan,
    title="Product Service",
    summary="API for managing products",
    description=OPENAPI_DESCRIPTION,
    version=settings.app.version,
    openapi_tags=OPENAPI_TAGS,
)

app.include_router(category_router)
app.include_router(product_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_requests)


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
                    "example": {"status": "ok", "version": "0.1.0"},
                }
            },
        },
    },
)
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
