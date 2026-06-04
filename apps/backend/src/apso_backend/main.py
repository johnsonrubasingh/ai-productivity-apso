from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apso_backend.api.router import api_router
from apso_backend.api.middleware import (
    access_log_and_metrics_middleware,
    rate_limit_middleware,
    request_id_middleware,
    unhandled_exception_middleware,
)
from apso_backend.core.config import get_settings
from apso_backend.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    app = FastAPI(
        title="APSO Backend API",
        version="0.1.0",
        description="AI-powered SDLC intelligence backend. MVP scope is read-only extraction and analysis.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(unhandled_exception_middleware)
    app.middleware("http")(access_log_and_metrics_middleware)
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(request_id_middleware)

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
