from __future__ import annotations

import builtins

import sqlalchemy as sa
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base(self, user_id: str) -> Select[tuple[Account]]:
        return select(Account).where(Account.user_id == user_id, Account.deleted_at.is_(None))

    async def list(self, user_id: str) -> builtins.list[Account]:
        res = await self._session.execute(self._base(user_id).order_by(Account.created_at.desc()))
        return list(res.scalars().all())

    async def list_paginated(
        self, *, user_id: str, limit: int, offset: int
    ) -> tuple[builtins.list[Account], int]:
        stmt = self._base(user_id).order_by(Account.created_at.desc())
        total_res = await self._session.execute(select(func.count()).select_from(stmt.subquery()))
        total = int(total_res.scalar_one())
        res = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(res.scalars().all()), total

    async def get(self, user_id: str, account_id: str) -> Account | None:
        res = await self._session.execute(self._base(user_id).where(Account.id == account_id))
        return res.scalar_one_or_none()

    async def create(self, account: Account) -> Account:
        self._session.add(account)
        await self._session.flush()
        return account

    async def update_balance(self, account_id: str, balance: object) -> None:
        await self._session.execute(
            update(Account).where(Account.id == account_id).values(balance=balance)
        )

    async def soft_delete(self, user_id: str, account_id: str) -> None:
        await self._session.execute(
            update(Account)
            .where(
                Account.user_id == user_id, Account.id == account_id, Account.deleted_at.is_(None)
            )
            .values(deleted_at=sa.func.now())
        )
