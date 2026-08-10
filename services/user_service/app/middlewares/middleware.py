from fastapi import Request

from datetime import datetime


def _create_request_log_data(
    request_id: str,
    method: str,
    url: str,
    path: str,
    query_params: dict[str, any],
    client_ip: str,
    user_agent: str,
    body: bytes,
    headers: dict[str, str],
) -> dict[str, any]:
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

def create_logging_middleware(logger):
    async def log_requests(request: Request, call_next):
        # Создаем данные для логирования запроса
        request_data = _create_request_log_data(
            request_id=getattr(request.state, "request_id", None),
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if hasattr(request, "client") else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            body=request.body,
            headers=dict(request.headers),
        )
        start = datetime.now()
        response = None
        try:
            response = await call_next(request)
            end = datetime.now()
            processing_time = (end - start).total_seconds() * 1000
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise    
        logger.info(
            f"{request_data} -> {response.status_code} time_exec: "
            f"[{processing_time:.3f}] ms"
        )
        return response

    return log_requests