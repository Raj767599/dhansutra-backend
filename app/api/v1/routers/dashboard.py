from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.domain.enums import TransactionType
from app.schemas.dashboard import (
    AccountOverviewItem,
    BudgetUsageItem,
    DashboardSummaryResponse,
    GoalSummaryItem,
    RecentTransactionItem,
    TopSpendingCategoryItem,
)
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard summary",
    description="Returns dashboard aggregates for the current user (balances, month totals, recent tx, goals, budgets, top categories).",
)
async def summary(
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> DashboardSummaryResponse:
    data = await DashboardService(session).summary(user=user)
    accounts = [
        AccountOverviewItem(
            account_id=a.id,
            name=a.name,
            currency=a.currency,
            balance=a.balance,
            archived=a.archived,
        )
        for a in data["account_overview"]
    ]
    recent = [
        RecentTransactionItem(
            id=t.id,
            type=TransactionType(t.type),
            amount=t.amount,
            currency=t.currency,
            occurred_at=t.occurred_at,
            account_id=t.account_id,
            category_id=t.category_id,
            merchant=t.merchant,
        )
        for t in data["recent_transactions"]
    ]
    goals = []
    for g in data["active_goals"]:
        progress = (
            (g.current_amount / g.target_amount * Decimal("100")).quantize(Decimal("0.01"))
            if g.target_amount > 0
            else Decimal("0")
        )
        goals.append(
            GoalSummaryItem(
                goal_id=g.id,
                name=g.name,
                target_amount=g.target_amount,
                current_amount=g.current_amount,
                currency=g.currency,
                deadline=g.deadline,
                completed=g.completed,
                progress_pct=progress,
            )
        )
    budgets = [BudgetUsageItem(**b) for b in data["budget_usage_summary"]]
    top = [TopSpendingCategoryItem(**c) for c in data["top_spending_categories"]]

    return DashboardSummaryResponse(
        total_balance=data["total_balance"],
        total_income_current_month=data["total_income_current_month"],
        total_expense_current_month=data["total_expense_current_month"],
        total_savings=data["total_savings"],
        budget_usage_summary=budgets,
        recent_transactions=recent,
        active_goals=goals,
        top_spending_categories=top,
        account_overview=accounts,
    )
