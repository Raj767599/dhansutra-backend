from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None


class UnauthorizedError(AppError):
    def __init__(
        self, message: str = "Unauthorized", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(code="unauthorized", message=message, status_code=401, details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", details: dict[str, Any] | None = None) -> None:
        super().__init__(code="forbidden", message=message, status_code=403, details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", details: dict[str, Any] | None = None) -> None:
        super().__init__(code="not_found", message=message, status_code=404, details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", details: dict[str, Any] | None = None) -> None:
        super().__init__(code="conflict", message=message, status_code=409, details=details)


class ValidationAppError(AppError):
    def __init__(
        self, message: str = "Validation failed", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(code="validation_error", message=message, status_code=422, details=details)
