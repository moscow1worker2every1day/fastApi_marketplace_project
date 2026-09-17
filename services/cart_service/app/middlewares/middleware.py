from fastapi import Request
from fastapi.responses import JSONResponse

from app.log import request_logger


def catch_server_error():
    async def try_request(request: Request, call_next):
        try:
            request_logger.info(f"Request received: {request.method} {request.url}")
            call_response = await call_next(request)
            return call_response
        except Exception as e:
            request_logger.error(f"Unhandled exception {e} for request {request.method} {request.url}")

            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Internal server error {e}"
                }
            )

    return try_request
