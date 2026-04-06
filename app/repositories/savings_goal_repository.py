from __future__ import annotations

import builtins

import sqlalchemy as sa
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.savings_goal import GoalContribution, SavingsGoal


class SavingsGoalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base(self, user_id: str) -> Select[tuple[SavingsGoal]]:
        return select(SavingsGoal).where(
            SavingsGoal.user_id == user_id, SavingsGoal.deleted_at.is_(None)
        )

    async def list(self, user_id: str) -> builtins.list[SavingsGoal]:
        res = await self._session.execute(
            self._base(user_id).order_by(SavingsGoal.created_at.desc())
        )
        return list(res.scalars().all())

    async def list_paginated(
        self, *, user_id: str, limit: int, offset: int
    ) -> tuple[builtins.list[SavingsGoal], int]:
        stmt = self._base(user_id).order_by(SavingsGoal.created_at.desc())
        total_res = await self._session.execute(select(func.count()).select_from(stmt.subquery()))
        total = int(total_res.scalar_one())
        res = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(res.scalars().all()), total

    async def get(self, user_id: str, goal_id: str) -> SavingsGoal | None:
        res = await self._session.execute(self._base(user_id).where(SavingsGoal.id == goal_id))
        return res.scalar_one_or_none()

    async def create(self, g: SavingsGoal) -> SavingsGoal:
        self._session.add(g)
        await self._session.flush()
        return g

    async def soft_delete(self, user_id: str, goal_id: str) -> None:
        await self._session.execute(
            update(SavingsGoal)
            .where(
                SavingsGoal.user_id == user_id,
                SavingsGoal.id == goal_id,
                SavingsGoal.deleted_at.is_(None),
            )
            .values(deleted_at=sa.func.now())
        )


class GoalContributionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_goal(self, goal_id: str) -> builtins.list[GoalContribution]:
        res = await self._session.execute(
            select(GoalContribution)
            .where(GoalContribution.goal_id == goal_id, GoalContribution.deleted_at.is_(None))
            .order_by(GoalContribution.contributed_at.desc())
        )
        return list(res.scalars().all())

    async def create(self, c: GoalContribution) -> GoalContribution:
        self._session.add(c)
        await self._session.flush()
        return c
