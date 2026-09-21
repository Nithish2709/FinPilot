from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.schemas.common import ErrorResponse

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception for FinPilot backend."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom AppException instances."""
    logger.warning("Application exception: %s (path: %s)", exc.message, request.url.path)
    error_payload = ErrorResponse(
        status="error",
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump(),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for standard HTTP exceptions."""
    logger.warning("HTTP exception %d: %s (path: %s)", exc.status_code, exc.detail, request.url.path)
    error_payload = ErrorResponse(
        status="error",
        message=str(exc.detail),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for request validation errors."""
    logger.warning("Validation error on path %s: %s", request.url.path, exc.errors())
    error_payload = ErrorResponse(
        status="error",
        message="Request validation failed",
        details=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_payload.model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unexpected internal server errors."""
    logger.error("Unhandled exception processing request %s: %s", request.url.path, exc, exc_info=True)
    error_payload = ErrorResponse(
        status="error",
        message="Internal server error",
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers exception handlers on the FastAPI application instance."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
