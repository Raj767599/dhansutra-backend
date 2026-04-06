from __future__ import annotations

import builtins
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.savings_goal import GoalContribution, SavingsGoal
from app.models.user import User
from app.repositories.savings_goal_repository import (
    GoalContributionRepository,
    SavingsGoalRepository,
)


class SavingsGoalService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._goals = SavingsGoalRepository(session)
        self._contrib = GoalContributionRepository(session)

    def _progress_pct(self, *, current: Decimal, target: Decimal) -> Decimal:
        if target <= 0:
            return Decimal("0")
        return (current / target * Decimal("100")).quantize(Decimal("0.01"))

    async def create(
        self,
        *,
        user: User,
        name: str,
        target_amount: Decimal,
        currency: str,
        deadline: datetime | None,
    ) -> SavingsGoal:
        g = SavingsGoal(
            user_id=user.id,
            name=name,
            target_amount=target_amount,
            current_amount=Decimal("0"),
            currency=currency.upper(),
            deadline=deadline.astimezone(timezone.utc) if deadline else None,
            completed=False,
        )
        await self._goals.create(g)
        await self._session.commit()
        return g

    async def list(self, *, user: User) -> builtins.list[SavingsGoal]:
        return await self._goals.list(user.id)

    async def list_paginated(
        self, *, user: User, limit: int, offset: int
    ) -> tuple[builtins.list[SavingsGoal], int]:
        return await self._goals.list_paginated(user_id=user.id, limit=limit, offset=offset)

    async def get(self, *, user: User, goal_id: str) -> SavingsGoal:
        g = await self._goals.get(user.id, goal_id)
        if g is None:
            raise NotFoundError("Goal not found")
        return g

    async def update(
        self,
        *,
        user: User,
        goal_id: str,
        name: str | None,
        target_amount: Decimal | None,
        deadline: datetime | None,
        completed: bool | None,
    ) -> SavingsGoal:
        g = await self.get(user=user, goal_id=goal_id)
        if name is not None:
            g.name = name
        if target_amount is not None:
            if target_amount <= 0:
                raise ValidationAppError(details={"target_amount": "Must be > 0"})
            g.target_amount = target_amount
        if deadline is not None:
            g.deadline = deadline.astimezone(timezone.utc)
        if completed is not None:
            g.completed = completed
        await self._session.commit()
        await self._session.refresh(g)
        return g

    async def delete(self, *, user: User, goal_id: str) -> None:
        await self.get(user=user, goal_id=goal_id)
        await self._goals.soft_delete(user.id, goal_id)
        await self._session.commit()

    async def add_contribution(
        self,
        *,
        user: User,
        goal_id: str,
        amount: Decimal,
        contributed_at: datetime,
        note: str | None,
    ) -> GoalContribution:
        g = await self.get(user=user, goal_id=goal_id)
        c = GoalContribution(
            goal_id=g.id,
            amount=amount,
            contributed_at=contributed_at.astimezone(timezone.utc),
            note=note,
        )
        await self._contrib.create(c)
        g.current_amount = (g.current_amount or Decimal("0")) + amount
        if g.current_amount >= g.target_amount:
            g.completed = True
        await self._session.commit()
        await self._session.refresh(g)
        return c

    async def get_with_contributions(
        self, *, user: User, goal_id: str
    ) -> tuple[SavingsGoal, builtins.list[GoalContribution]]:
        g = await self.get(user=user, goal_id=goal_id)
        contrib = await self._contrib.list_for_goal(g.id)
        return g, contrib

    async def list_with_contributions(
        self, *, user: User
    ) -> builtins.list[tuple[SavingsGoal, builtins.list[GoalContribution]]]:
        goals = await self.list(user=user)
        out: builtins.list[tuple[SavingsGoal, builtins.list[GoalContribution]]] = []
        for g in goals:
            out.append((g, await self._contrib.list_for_goal(g.id)))
        return out

    async def list_with_contributions_paginated(
        self, *, user: User, limit: int, offset: int
    ) -> tuple[
        builtins.list[tuple[SavingsGoal, builtins.list[GoalContribution]]],
        int,
    ]:
        goals, total = await self.list_paginated(user=user, limit=limit, offset=offset)
        out: builtins.list[tuple[SavingsGoal, builtins.list[GoalContribution]]] = []
        for g in goals:
            out.append((g, await self._contrib.list_for_goal(g.id)))
        return out, total
