from enum import Enum
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.orders import router as orders_router

app = FastAPI()

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
async def read_order(order_type: OrderType, order_id: int):
    if order_type is OrderType.order_type3:
        pass
    else:
        return {"order_type": order_type.value, "order_id": order_id}
