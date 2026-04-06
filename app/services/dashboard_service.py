from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AccountType, TransactionType
from app.models.account import Account
from app.models.budget import Budget
from app.models.category import Category
from app.models.savings_goal import SavingsGoal
from app.models.transaction import Transaction
from app.models.user import User
from app.services.budget_service import BudgetService
from app.utils.datetime import current_month_bounds_utc


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._budgets = BudgetService(session)

    async def summary(self, *, user: User) -> dict[str, object]:
        # Accounts overview + totals
        acc_stmt = select(Account).where(Account.user_id == user.id, Account.deleted_at.is_(None))
        acc_res = await self._session.execute(acc_stmt)
        accounts = list(acc_res.scalars().all())

        total_balance = sum((a.balance or Decimal("0")) for a in accounts if not a.archived)
        total_savings = sum(
            (a.balance or Decimal("0"))
            for a in accounts
            if (not a.archived and a.type == AccountType.savings.value)
        )

        start_month, end_month = current_month_bounds_utc()
        t = Transaction
        base = sa.and_(
            t.user_id == user.id,
            t.deleted_at.is_(None),
            t.occurred_at >= start_month,
            t.occurred_at < end_month,
        )
        income_res = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.income.value
            )
        )
        expense_res = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.expense.value
            )
        )
        total_income_current_month = Decimal(str(income_res.scalar_one()))
        total_expense_current_month = Decimal(str(expense_res.scalar_one()))

        # Recent transactions
        recent_res = await self._session.execute(
            select(Transaction)
            .where(Transaction.user_id == user.id, Transaction.deleted_at.is_(None))
            .order_by(Transaction.occurred_at.desc())
            .limit(10)
        )
        recent = list(recent_res.scalars().all())

        # Active goals
        goals_res = await self._session.execute(
            select(SavingsGoal)
            .where(SavingsGoal.user_id == user.id, SavingsGoal.deleted_at.is_(None))
            .order_by(SavingsGoal.completed.asc(), SavingsGoal.deadline.asc().nullslast())
            .limit(10)
        )
        goals = list(goals_res.scalars().all())

        # Top spending categories current month
        c = Category
        top_res = await self._session.execute(
            select(c.id, c.name, func.coalesce(func.sum(t.amount), 0).label("total"))
            .select_from(t)
            .join(c, c.id == t.category_id)
            .where(base, t.type == TransactionType.expense.value, t.category_id.is_not(None))
            .group_by(c.id, c.name)
            .order_by(sa.desc("total"))
            .limit(5)
        )
        top = [
            {"category_id": r[0], "category_name": r[1], "total_spent": Decimal(str(r[2]))}
            for r in top_res.all()
        ]

        # Budget usage current month
        now = datetime.now(timezone.utc)
        bud_stmt = select(Budget).where(
            Budget.user_id == user.id,
            Budget.deleted_at.is_(None),
            Budget.year == now.year,
            Budget.month == now.month,
        )
        bud_res = await self._session.execute(bud_stmt)
        budgets = list(bud_res.scalars().all())
        budget_usage: list[dict[str, object]] = []
        for b in budgets:
            row = await self._budgets.get(user=user, budget_id=b.id)
            budget_usage.append(
                {
                    "budget_id": b.id,
                    "year": b.year,
                    "month": b.month,
                    "amount": b.amount,
                    "spent": row["spent"],
                    "remaining": row["remaining"],
                    "usage_pct": row["usage_pct"],
                    "is_over_budget": row["is_over_budget"],
                    "category_id": b.category_id,
                }
            )

        return {
            "total_balance": total_balance,
            "total_income_current_month": total_income_current_month,
            "total_expense_current_month": total_expense_current_month,
            "total_savings": total_savings,
            "budget_usage_summary": budget_usage,
            "recent_transactions": recent,
            "active_goals": goals,
            "top_spending_categories": top,
            "account_overview": accounts,
        }
