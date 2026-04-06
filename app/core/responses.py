from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: dict[str, Any] = Field(
        ...,
        examples=[
            {
                "code": "validation_error",
                "message": "Validation failed",
                "details": {"field": "reason"},
            }
        ],
    )


class PageMeta(BaseModel):
    limit: int
    offset: int
    total: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta
