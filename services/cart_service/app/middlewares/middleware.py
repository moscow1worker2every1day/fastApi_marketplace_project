from fastapi import Request
from fastapi.responses import JSONResponse

from app.logging import log


def catch_server_error():
    async def try_request(request: Request, call_next):
        try:
            call_response = await call_next(request)
            return call_response
        except Exception as e:
            log.error(f"Unhandled exception {e}")

            return JSONResponse(
                status_code=500,
                content={
                    "detail": f"Internal server error {e}"
                }
            )

    return try_request
