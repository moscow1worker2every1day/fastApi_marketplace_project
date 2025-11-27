from fastapi import HTTPException, status, Request


def error_handler_middleware():
    async def try_request(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(f"Internal server error: {str(exc)}")
            )
    return try_request
