from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError

logger = logging.getLogger("app.errors")


def _json_error(
    code: str, message: str, *, details: dict[str, Any] | None = None, status: int
) -> JSONResponse:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return _json_error(exc.code, exc.message, details=exc.details, status=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = {"errors": exc.errors()}
        return _json_error("validation_error", "Validation failed", details=details, status=422)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error", extra={"extra": {"error_type": type(exc).__name__}})
        return _json_error("internal_error", "Internal server error", status=500)
