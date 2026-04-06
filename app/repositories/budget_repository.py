from __future__ import annotations

import builtins

import sqlalchemy as sa
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget


class BudgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base(self, user_id: str) -> Select[tuple[Budget]]:
        return select(Budget).where(Budget.user_id == user_id, Budget.deleted_at.is_(None))

    async def list(self, user_id: str) -> builtins.list[Budget]:
        res = await self._session.execute(
            self._base(user_id).order_by(Budget.year.desc(), Budget.month.desc())
        )
        return list(res.scalars().all())

    async def list_paginated(
        self, *, user_id: str, limit: int, offset: int
    ) -> tuple[builtins.list[Budget], int]:
        stmt = self._base(user_id).order_by(Budget.year.desc(), Budget.month.desc())
        total_res = await self._session.execute(select(func.count()).select_from(stmt.subquery()))
        total = int(total_res.scalar_one())
        res = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(res.scalars().all()), total

    async def get(self, user_id: str, budget_id: str) -> Budget | None:
        res = await self._session.execute(self._base(user_id).where(Budget.id == budget_id))
        return res.scalar_one_or_none()

    async def create(self, b: Budget) -> Budget:
        self._session.add(b)
        await self._session.flush()
        return b

    async def soft_delete(self, user_id: str, budget_id: str) -> None:
        await self._session.execute(
            update(Budget)
            .where(Budget.user_id == user_id, Budget.id == budget_id, Budget.deleted_at.is_(None))
            .values(deleted_at=sa.func.now())
        )
