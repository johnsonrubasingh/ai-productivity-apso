from collections.abc import Awaitable, Callable
import logging
from time import perf_counter

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from apso_backend.core.metrics import metrics_registry
from apso_backend.core.rate_limit import RateLimiter
from apso_backend.core.request_id import new_request_id, set_request_id
from apso_backend.core.config import get_settings


logger = logging.getLogger("apso.request")
settings = get_settings()
rate_limiter = RateLimiter(
    max_requests=settings.security.rate_limit_requests,
    window_seconds=settings.security.rate_limit_window_seconds,
)


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("x-request-id") or new_request_id()
    set_request_id(request_id)
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


async def access_log_and_metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - started) * 1000, 2)
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    metrics_registry.record_request(request.method, path, response.status_code, duration_ms)
    logger.info(
        "http_request",
        extra={
            "method": request.method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_host": request.client.host if request.client else None,
        },
    )
    response.headers["x-apso-duration-ms"] = str(duration_ms)
    return response


async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path.endswith("/health") or request.url.path.endswith("/ops/metrics"):
        return await call_next(request)

    key = request.headers.get("authorization") or request.headers.get("x-user-id")
    if not key:
        key = request.client.host if request.client else "unknown"
    allowed, remaining = rate_limiter.allow(key)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests. Retry after the rate-limit window.",
                    "request_id": request.headers.get("x-request-id"),
                }
            },
            headers={"x-ratelimit-remaining": "0"},
        )
    response = await call_next(request)
    response.headers["x-ratelimit-remaining"] = str(remaining)
    return response


async def unhandled_exception_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    try:
        return await call_next(request)
    except Exception:
        request_id = request.headers.get("x-request-id") or new_request_id()
        logger.exception("unhandled_exception", extra={"method": request.method, "path": request.url.path})
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected backend error occurred.",
                    "request_id": request_id,
                }
            },
            headers={"x-request-id": request_id},
        )
