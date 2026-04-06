from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.constants import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT


class PaginationParams(BaseModel):
    limit: int = Field(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT)
    offset: int = Field(default=0, ge=0)
