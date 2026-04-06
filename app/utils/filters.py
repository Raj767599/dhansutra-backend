from __future__ import annotations

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start: str | None = Field(default=None, description="ISO datetime start (inclusive)")
    end: str | None = Field(default=None, description="ISO datetime end (exclusive)")
