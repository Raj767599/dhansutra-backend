from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.enums import TransactionType
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.user import User
from app.services.budget_service import BudgetService


@pytest.mark.anyio
async def test_budget_spent_calculation(app, account_category_fixtures) -> None:
    async for s in app.state.db.session():
        user = await s.get(User, account_category_fixtures["user_id"])
        assert user is not None

        now = datetime.now(timezone.utc)
        b = Budget(
            user_id=user.id,
            year=now.year,
            month=now.month,
            amount=Decimal("100.00"),
            currency="USD",
            category_id=account_category_fixtures["expense_cat_id"],
        )
        s.add(b)
        await s.flush()

        s.add(
            Transaction(
                user_id=user.id,
                type=TransactionType.expense.value,
                amount=Decimal("30.00"),
                currency="USD",
                occurred_at=now,
                account_id=account_category_fixtures["account_id"],
                destination_account_id=None,
                category_id=account_category_fixtures["expense_cat_id"],
            )
        )
        await s.commit()

        row = await BudgetService(s).get(user=user, budget_id=b.id)
        assert row["spent"] == Decimal("30.00")
