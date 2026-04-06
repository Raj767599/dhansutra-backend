from __future__ import annotations

import builtins
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.domain.enums import AccountType
from app.models.account import Account
from app.models.user import User
from app.repositories.account_repository import AccountRepository


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._accounts = AccountRepository(session)

    async def create(
        self,
        *,
        user: User,
        name: str,
        type: AccountType,
        currency: str,
        initial_balance: Decimal,
        archived: bool,
        allow_transactions_when_archived: bool,
    ) -> Account:
        if initial_balance < 0:
            raise ValidationAppError(details={"initial_balance": "Must be >= 0"})
        account = Account(
            user_id=user.id,
            name=name,
            type=type.value,
            currency=currency.upper(),
            balance=initial_balance,
            archived=archived,
            allow_transactions_when_archived=allow_transactions_when_archived,
        )
        await self._accounts.create(account)
        await self._session.commit()
        return account

    async def list(self, *, user: User) -> builtins.list[Account]:
        return await self._accounts.list(user.id)

    async def list_paginated(
        self, *, user: User, limit: int, offset: int
    ) -> tuple[builtins.list[Account], int]:
        return await self._accounts.list_paginated(user_id=user.id, limit=limit, offset=offset)

    async def get(self, *, user: User, account_id: str) -> Account:
        account = await self._accounts.get(user.id, account_id)
        if account is None:
            raise NotFoundError("Account not found")
        return account

    async def update(
        self,
        *,
        user: User,
        account_id: str,
        name: str | None,
        archived: bool | None,
        allow_transactions_when_archived: bool | None,
    ) -> Account:
        account = await self.get(user=user, account_id=account_id)
        if name is not None:
            account.name = name
        if archived is not None:
            account.archived = archived
        if allow_transactions_when_archived is not None:
            account.allow_transactions_when_archived = allow_transactions_when_archived
        await self._session.commit()
        await self._session.refresh(account)
        return account

    async def delete(self, *, user: User, account_id: str) -> None:
        account = await self.get(user=user, account_id=account_id)
        account.deleted_at = (
            account.deleted_at or account.updated_at
        )  # soft-delete marker; updated in DB
        # For SQLite simplicity, set deleted_at = now() using SQL expression
        import sqlalchemy as sa

        await self._session.execute(
            sa.update(Account)
            .where(
                Account.user_id == user.id, Account.id == account_id, Account.deleted_at.is_(None)
            )
            .values(deleted_at=sa.func.now())
        )
        await self._session.commit()
