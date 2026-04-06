from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SpendingByCategoryItem(BaseModel):
    category_id: str
    category_name: str
    total: Decimal


class SpendingByCategoryResponse(BaseModel):
    start: datetime
    end: datetime
    items: list[SpendingByCategoryItem]


class MonthlyTrendItem(BaseModel):
    year: int
    month: int
    income: Decimal
    expense: Decimal
    net: Decimal


class MonthlyTrendResponse(BaseModel):
    items: list[MonthlyTrendItem]


class CashflowResponse(BaseModel):
    start: datetime
    end: datetime
    income: Decimal
    expense: Decimal
    net: Decimal


class TopCategoryItem(BaseModel):
    category_id: str
    category_name: str
    total_spent: Decimal


class TopCategoriesResponse(BaseModel):
    start: datetime
    end: datetime
    items: list[TopCategoryItem]
