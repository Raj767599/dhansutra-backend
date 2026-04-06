from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.enums import TransactionType
from app.models.account import Account
from app.models.user import User
from app.services.transaction_service import TransactionService


@pytest.mark.anyio
async def test_transaction_service_reversal(app, account_category_fixtures) -> None:
    async for s in app.state.db.session():
        user = await s.get(User, account_category_fixtures["user_id"])
        assert user is not None
        svc = TransactionService(s)
        tx = await svc.create(
            user=user,
            type=TransactionType.expense,
            amount=Decimal("10.00"),
            occurred_at=datetime.now(timezone.utc),
            account_id=account_category_fixtures["account_id"],
            category_id=account_category_fixtures["expense_cat_id"],
            destination_account_id=None,
            note=None,
            merchant=None,
            recurring_template=None,
        )
        acc = await s.get(Account, account_category_fixtures["account_id"])
        assert acc is not None
        assert acc.balance == Decimal("990.00")

        await svc.delete(user=user, transaction_id=tx.id)
        acc2 = await s.get(Account, account_category_fixtures["account_id"])
        assert acc2 is not None
        assert acc2.balance == Decimal("1000.00")
