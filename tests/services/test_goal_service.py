from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models.user import User
from app.services.savings_goal_service import SavingsGoalService


@pytest.mark.anyio
async def test_goal_contribution_progress(app, seeded_user) -> None:
    async for s in app.state.db.session():
        user = await s.get(User, seeded_user.id)
        assert user is not None
        svc = SavingsGoalService(s)
        g = await svc.create(
            user=user, name="G", target_amount=Decimal("100.00"), currency="USD", deadline=None
        )
        await svc.add_contribution(
            user=user,
            goal_id=g.id,
            amount=Decimal("100.00"),
            contributed_at=datetime.now(timezone.utc),
            note=None,
        )
        g2 = await svc.get(user=user, goal_id=g.id)
        assert g2.current_amount == Decimal("100.00")
        assert g2.completed is True
