from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SavingsGoalCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Emergency Fund"])
    target_amount: Decimal = Field(..., gt=0, examples=["2000.00"])
    currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])
    deadline: datetime | None = Field(default=None, examples=["2026-12-31T00:00:00Z"])


class SavingsGoalUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    target_amount: Decimal | None = Field(default=None, gt=0)
    deadline: datetime | None = None
    completed: bool | None = None


class GoalContributionCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, examples=["50.00"])
    contributed_at: datetime = Field(..., examples=["2026-04-06T12:00:00Z"])
    note: str | None = Field(default=None, max_length=500)


class GoalContributionResponse(BaseModel):
    id: str
    amount: Decimal
    contributed_at: datetime
    note: str | None


class SavingsGoalResponse(BaseModel):
    id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    deadline: datetime | None
    completed: bool
    progress_pct: Decimal
    contributions: list[GoalContributionResponse] = []
