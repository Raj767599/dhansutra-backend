from __future__ import annotations

import builtins
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.domain.enums import CategoryType, TransactionType
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.utils.datetime import month_bounds_utc


class BudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._budgets = BudgetRepository(session)
        self._categories = CategoryRepository(session)

    async def _spent(
        self, *, user: User, year: int, month: int, category_id: str | None
    ) -> Decimal:
        start, end = month_bounds_utc(year, month)
        t = Transaction
        where = [
            t.user_id == user.id,
            t.deleted_at.is_(None),
            t.type == TransactionType.expense.value,
            t.occurred_at >= start,
            t.occurred_at < end,
        ]
        if category_id is not None:
            where.append(t.category_id == category_id)
        res = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(*where)
        )
        return Decimal(str(res.scalar_one()))

    def _calc(self, *, amount: Decimal, spent: Decimal) -> tuple[Decimal, Decimal, Decimal, bool]:
        remaining = amount - spent
        usage = (spent / amount * Decimal("100")) if amount > 0 else Decimal("0")
        usage_pct = usage.quantize(Decimal("0.01"))
        return spent, remaining, usage_pct, remaining < 0

    async def create(
        self,
        *,
        user: User,
        year: int,
        month: int,
        amount: Decimal,
        currency: str,
        category_id: str | None,
    ) -> Budget:
        if category_id is not None:
            cat = await self._categories.get(user.id, category_id)
            if cat is None:
                raise ValidationAppError(details={"category_id": "Category not found"})
            if CategoryType(cat.type) != CategoryType.expense:
                raise ValidationAppError(
                    details={"category_id": "Budget category must be expense type"}
                )

        b = Budget(
            user_id=user.id,
            year=year,
            month=month,
            amount=amount,
            currency=currency.upper(),
            category_id=category_id,
        )
        await self._budgets.create(b)
        await self._session.commit()
        return b

    async def list(self, *, user: User) -> builtins.list[dict[str, object]]:
        budgets = await self._budgets.list(user.id)
        items: list[dict[str, object]] = []
        for b in budgets:
            spent = await self._spent(
                user=user, year=b.year, month=b.month, category_id=b.category_id
            )
            spent_v, remaining, usage_pct, is_over = self._calc(amount=b.amount, spent=spent)
            items.append(
                {
                    "budget": b,
                    "spent": spent_v,
                    "remaining": remaining,
                    "usage_pct": usage_pct,
                    "is_over_budget": is_over,
                }
            )
        return items

    async def list_paginated(
        self, *, user: User, limit: int, offset: int
    ) -> tuple[builtins.list[dict[str, object]], int]:
        budgets, total = await self._budgets.list_paginated(
            user_id=user.id, limit=limit, offset=offset
        )
        items: list[dict[str, object]] = []
        for b in budgets:
            spent = await self._spent(
                user=user, year=b.year, month=b.month, category_id=b.category_id
            )
            spent_v, remaining, usage_pct, is_over = self._calc(amount=b.amount, spent=spent)
            items.append(
                {
                    "budget": b,
                    "spent": spent_v,
                    "remaining": remaining,
                    "usage_pct": usage_pct,
                    "is_over_budget": is_over,
                }
            )
        return items, total

    async def get(self, *, user: User, budget_id: str) -> dict[str, object]:
        b = await self._budgets.get(user.id, budget_id)
        if b is None:
            raise NotFoundError("Budget not found")
        spent = await self._spent(user=user, year=b.year, month=b.month, category_id=b.category_id)
        spent_v, remaining, usage_pct, is_over = self._calc(amount=b.amount, spent=spent)
        return {
            "budget": b,
            "spent": spent_v,
            "remaining": remaining,
            "usage_pct": usage_pct,
            "is_over_budget": is_over,
        }

    async def update(self, *, user: User, budget_id: str, amount: Decimal | None) -> Budget:
        b = await self._budgets.get(user.id, budget_id)
        if b is None:
            raise NotFoundError("Budget not found")
        if amount is not None:
            b.amount = amount
        await self._session.commit()
        await self._session.refresh(b)
        return b

    async def delete(self, *, user: User, budget_id: str) -> None:
        b = await self._budgets.get(user.id, budget_id)
        if b is None:
            raise NotFoundError("Budget not found")
        await self._budgets.soft_delete(user.id, budget_id)
        await self._session.commit()
