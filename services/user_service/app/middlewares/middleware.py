from datetime import datetime

from fastapi import Request

from app.log import request_logger


async def _create_request_log_data(
    request: Request,
) -> dict:
    """Create simplified data for request logging."""
    data = {
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "headers": dict(request.headers),
    }
    if request.query_params:
        data["query_params"] = dict(request.query_params)
    if body := await request.body():
        data["body"] = body.decode(errors="ignore")
    return data

async def log_requests(request: Request, call_next):
    """
    Writes one log for each request.

    - INFO  → requests.log (+ slow_requests.log if threshold is exceeded)
    - ERROR → requests.log + errors.log
    """
    request_data = await _create_request_log_data(request)
    start = datetime.now()
    try:
        response = await call_next(request)
        processing_time = (datetime.now() - start).total_seconds()
        # processing_time in extra → slow_requests will filter it out
        request_logger.bind(processing_time=processing_time).info(
            f"{request_data} -> {response.status_code} "
            f"time_exec: [{processing_time * 1000:.3f}] ms"
        )
        return response
    except Exception as e:
        processing_time = (datetime.now() - start).total_seconds()
        request_logger.bind(processing_time=processing_time).opt(exception=True).error(
            f"Error processing request: {e} "
            f"time_exec: [{processing_time * 1000:.3f}] ms"
        )
        raise
