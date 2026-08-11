from datetime import datetime

from fastapi import Request

from app.log import logger


def _create_request_log_data(
    request_id: str | None,
    method: str,
    url: str,
    path: str,
    query_params: dict,
    client_ip: str,
    user_agent: str,
    body: bytes,
    headers: dict[str, str],
) -> dict:
    """Create simplified data for request logging."""
    body_str = body.decode(errors="ignore") if body else ""
    return {
        "request_id": request_id,
        "method": method,
        "url": url,
        "path": path,
        "query_params": query_params,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "content_length": str(len(body)),
        "body_preview": body_str,
        "headers": headers,
    }


async def log_requests(request: Request, call_next):
    """Пишет один лог на запрос; sinks сами раскладывают по files."""
    body = await request.body()
    request_id = getattr(request.state, "request_id", None) or "-"
    request_data = _create_request_log_data(
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        path=request.url.path,
        query_params=dict(request.query_params),
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        body=body,
        headers=dict(request.headers),
    )
    start = datetime.now()
    log = logger.bind(request_id=request_id)
    try:
        response = await call_next(request)
        processing_time = (datetime.now() - start).total_seconds()
        # processing_time в extra → slow_requests sink отфильтрует сам
        log.bind(processing_time=processing_time).info(
            f"{request_data} -> {response.status_code} "
            f"time_exec: [{processing_time * 1000:.3f}] ms"
        )
        return response
    except Exception as e:
        processing_time = (datetime.now() - start).total_seconds()
        log.bind(processing_time=processing_time).opt(exception=True).error(
            f"Error processing request: {e} "
            f"time_exec: [{processing_time * 1000:.3f}] ms"
        )
        raise
