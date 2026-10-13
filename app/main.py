"""FastAPI application entry point for the retrieval service foundation."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from uuid import uuid4

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import Settings, get_settings
from app.db.session import DatabaseManager
from app.observability.logging import configure_logging

REQUEST_ID_HEADER = "X-Request-ID"


@dataclass
class ApplicationResources:
    """Resources owned by the application lifespan."""

    database: DatabaseManager

    async def close(self) -> None:
        await self.database.close()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to logs and responses without logging request data."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def _error_response(request: Request, code: str, message: str, status_code: int) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "request_id": request_id},
    )


async def _request_validation_handler(
    request: Request,
    _exc: Exception,
) -> JSONResponse:
    return _error_response(request, "invalid_request", "Request validation failed", 422)


async def _http_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, HTTPException):
        return _error_response(request, "http_error", "Request failed", 500)
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(request, "http_error", message, exc.status_code)


async def _unhandled_exception_handler(
    request: Request,
    _exc: Exception,
) -> JSONResponse:
    return _error_response(request, "internal_error", "Internal server error", 500)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Validate configuration and own application resources for the process."""

    settings: Settings = app.state.settings
    settings.validate_startup()
    database_manager: DatabaseManager | None = app.state.database_manager
    if database_manager is None:
        database_manager = DatabaseManager.from_settings(settings.database)
    app.state.resources = ApplicationResources(database=database_manager)
    try:
        yield
    finally:
        await app.state.resources.close()
        app.state.resources = None


def create_app(
    settings: Settings | None = None,
    database_manager: DatabaseManager | None = None,
) -> FastAPI:
    """Create the application without importing models or connecting at import time."""

    configure_logging()
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title="RAG SLM Retrieval Service",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.database_manager = database_manager
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(RequestValidationError, _request_validation_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)

    @app.get("/health", tags=["operations"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", tags=["operations"])
    async def ready(request: Request) -> Response:
        resources: ApplicationResources = request.app.state.resources
        try:
            health = await resources.database.health()
        except (SQLAlchemyError, OSError):
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "checks": {"configuration": "ok", "database": "unavailable"},
                },
            )
        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "checks": {
                    "configuration": "ok",
                    "database": "connected",
                },
                "table_count": health.table_count,
            },
        )

    return app


__all__ = ["create_app"]
