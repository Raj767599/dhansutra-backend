from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class Money(BaseModel):
    amount: Decimal = Field(..., examples=["12.34"])
    currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])


class Timestamped(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
