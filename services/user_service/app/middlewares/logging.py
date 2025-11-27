from fastapi import Request
import time

def create_logging_middleware(logger):
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        end = time.time()
        logger.info(f"{request.method} {request.url} -> "
                    f"{response.status_code} time_exec: [{end - start:.3f}] ms")
        return response
    return log_requests