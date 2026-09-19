from contextlib import asynccontextmanager
from enum import Enum
from uuid import UUID

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.orders import router as orders_router
from app.log import configure_logging, startup_logger
from app.storage.postgresql.connection import DatabaseManager

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Check DB connection and apply Alembic migrations on startup."""
    startup_logger.info("Startup order-service")
    try:
        async with DatabaseManager.session_factory() as session:
            startup_logger.info("Checking the database connection...")
            await DatabaseManager.check_connection(session)
            startup_logger.info("Running database migrations...")
            await DatabaseManager.run_migrations(session)
    except Exception as e:
        startup_logger.error(
            "Connection to the database failed: "
            f"{type(e).__name__} - {e}."
        )
        raise

    startup_logger.info("Service is ready to accept requests.")
    yield
    startup_logger.info("Shutting down service...")


app = FastAPI(lifespan=lifespan)

app.include_router(orders_router)


class OrderType(str, Enum):
    order_type1 = "hand"
    order_type2 = "car"
    order_type3 = "auto"


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc: RequestValidationError):
    """Handler стандартного исключения validation error"""
    message = dict()
    for (i, error) in enumerate(exc.errors()):
        message[f"Validation error {i+1}"] = {"Field": f"{error['loc']}", "Error": f"{error['msg']}"}
    return JSONResponse(message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


# pass указывает что переменная соответствует любому пути
@app.get("/orders/{order_type}/{order_id:path}")
async def read_order(order_type: OrderType, order_id: UUID):
    if order_type is OrderType.order_type3:
        pass
    else:
        return {"order_type": order_type.value, "order_id": order_id}
