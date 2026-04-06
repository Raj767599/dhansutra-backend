from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.domain.enums import TransactionType


class AccountOverviewItem(BaseModel):
    account_id: str
    name: str
    currency: str
    balance: Decimal
    archived: bool


class BudgetUsageItem(BaseModel):
    budget_id: str
    year: int
    month: int
    amount: Decimal
    spent: Decimal
    remaining: Decimal
    usage_pct: Decimal
    is_over_budget: bool
    category_id: str | None


class RecentTransactionItem(BaseModel):
    id: str
    type: TransactionType
    amount: Decimal
    currency: str
    occurred_at: datetime
    account_id: str
    category_id: str | None
    merchant: str | None


class GoalSummaryItem(BaseModel):
    goal_id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    deadline: datetime | None
    completed: bool
    progress_pct: Decimal


class TopSpendingCategoryItem(BaseModel):
    category_id: str
    category_name: str
    total_spent: Decimal


class DashboardSummaryResponse(BaseModel):
    total_balance: Decimal
    total_income_current_month: Decimal
    total_expense_current_month: Decimal
    total_savings: Decimal
    budget_usage_summary: list[BudgetUsageItem]
    recent_transactions: list[RecentTransactionItem]
    active_goals: list[GoalSummaryItem]
    top_spending_categories: list[TopSpendingCategoryItem]
    account_overview: list[AccountOverviewItem]
