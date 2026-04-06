from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import TransactionType
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.utils.datetime import utc_now


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _range(self, start: datetime | None, end: datetime | None) -> tuple[datetime, datetime]:
        s = start or datetime(1970, 1, 1, tzinfo=timezone.utc)
        e = end or utc_now()
        return s, e

    async def spending_by_category(
        self, *, user: User, start: datetime | None, end: datetime | None
    ) -> dict[str, object]:
        s, e = self._range(start, end)
        t = Transaction
        c = Category
        res = await self._session.execute(
            select(c.id, c.name, func.coalesce(func.sum(t.amount), 0).label("total"))
            .select_from(t)
            .join(c, c.id == t.category_id)
            .where(
                t.user_id == user.id,
                t.deleted_at.is_(None),
                t.type == TransactionType.expense.value,
                t.occurred_at >= s,
                t.occurred_at < e,
            )
            .group_by(c.id, c.name)
            .order_by(sa.desc("total"))
        )
        items = [
            {"category_id": r[0], "category_name": r[1], "total": Decimal(str(r[2]))}
            for r in res.all()
        ]
        return {"start": s, "end": e, "items": items}

    async def cashflow(
        self, *, user: User, start: datetime | None, end: datetime | None
    ) -> dict[str, object]:
        s, e = self._range(start, end)
        t = Transaction
        base = sa.and_(
            t.user_id == user.id, t.deleted_at.is_(None), t.occurred_at >= s, t.occurred_at < e
        )
        inc = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.income.value
            )
        )
        exp = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.expense.value
            )
        )
        income = Decimal(str(inc.scalar_one()))
        expense = Decimal(str(exp.scalar_one()))
        return {"start": s, "end": e, "income": income, "expense": expense, "net": income - expense}

    async def top_categories(
        self, *, user: User, start: datetime | None, end: datetime | None, limit: int
    ) -> dict[str, object]:
        s, e = self._range(start, end)
        t = Transaction
        c = Category
        res = await self._session.execute(
            select(c.id, c.name, func.coalesce(func.sum(t.amount), 0).label("total"))
            .select_from(t)
            .join(c, c.id == t.category_id)
            .where(
                t.user_id == user.id,
                t.deleted_at.is_(None),
                t.type == TransactionType.expense.value,
                t.occurred_at >= s,
                t.occurred_at < e,
            )
            .group_by(c.id, c.name)
            .order_by(sa.desc("total"))
            .limit(limit)
        )
        items = [
            {"category_id": r[0], "category_name": r[1], "total_spent": Decimal(str(r[2]))}
            for r in res.all()
        ]
        return {"start": s, "end": e, "items": items}

    async def monthly_trend(self, *, user: User, months: int = 12) -> dict[str, object]:
        # SQLite: use strftime to group by year-month
        t = Transaction
        ym = func.strftime("%Y-%m", t.occurred_at)
        res = await self._session.execute(
            select(
                ym.label("ym"),
                func.coalesce(
                    func.sum(sa.case((t.type == TransactionType.income.value, t.amount), else_=0)),
                    0,
                ).label("income"),
                func.coalesce(
                    func.sum(sa.case((t.type == TransactionType.expense.value, t.amount), else_=0)),
                    0,
                ).label("expense"),
            )
            .where(t.user_id == user.id, t.deleted_at.is_(None))
            .group_by("ym")
            .order_by(sa.desc("ym"))
            .limit(months)
        )
        items = []
        for r in res.all():
            year_s, month_s = str(r[0]).split("-")
            income = Decimal(str(r[1]))
            expense = Decimal(str(r[2]))
            items.append(
                {
                    "year": int(year_s),
                    "month": int(month_s),
                    "income": income,
                    "expense": expense,
                    "net": income - expense,
                }
            )
        return {"items": list(reversed(items))}
