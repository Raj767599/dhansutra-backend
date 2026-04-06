from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreateRequest(BaseModel):
    year: int = Field(..., ge=2000, le=2100, examples=[2026])
    month: int = Field(..., ge=1, le=12, examples=[4])
    amount: Decimal = Field(..., gt=0, examples=["500.00"])
    currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])
    category_id: str | None = Field(
        default=None, description="Optional expense category for category-specific budget"
    )


class BudgetUpdateRequest(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)


class BudgetResponse(BaseModel):
    id: str
    year: int
    month: int
    amount: Decimal
    currency: str
    category_id: str | None

    spent: Decimal
    remaining: Decimal
    usage_pct: Decimal
    is_over_budget: bool
