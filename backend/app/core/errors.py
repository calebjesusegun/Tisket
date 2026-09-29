"""Centralised error types and handlers.

Every error response has the shape:
    {"error": {"code": str, "message": str, "details": list | None}}
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class BadRequestError(AppError):
    pass


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


_HTTP_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    429: "too_many_requests",
}


def error_body(
    code: str, message: str, details: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details}}


def _format_validation_errors(exc: RequestValidationError) -> list[dict[str, Any]]:
    details = []
    for err in exc.errors():
        loc = [str(part) for part in err.get("loc", ()) if part not in ("body",)]
        details.append({"field": ".".join(loc), "message": err.get("msg", "Invalid value")})
    return details


async def _app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(
        status_code=exc.status_code, content=error_body(exc.code, exc.message, exc.details)
    )


async def _validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    details = _format_validation_errors(exc)
    first = details[0] if details else None
    message = (
        f"{first['field']}: {first['message']}" if first and first["field"] else "Invalid request"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_body("validation_error", message, details),
    )


async def _http_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = _HTTP_CODES.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, str(exc.detail)),
        headers=getattr(exc, "headers", None),
    )


async def _unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_body("internal_error", "Something went wrong. Please try again."),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
