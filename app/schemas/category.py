from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import CategoryType


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80, examples=["Groceries"])
    type: CategoryType
    icon: str | None = Field(default=None, max_length=80, examples=["cart"])
    color: str | None = Field(default=None, max_length=16, examples=["#22c55e"])


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    icon: str | None = Field(default=None, max_length=80)
    color: str | None = Field(default=None, max_length=16)


class CategoryResponse(BaseModel):
    id: str
    name: str
    type: CategoryType
    icon: str | None
    color: str | None
    is_system: bool
