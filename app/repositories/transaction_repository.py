from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base(self, user_id: str) -> Select[tuple[Transaction]]:
        return select(Transaction).where(
            Transaction.user_id == user_id, Transaction.deleted_at.is_(None)
        )

    async def get(self, user_id: str, transaction_id: str) -> Transaction | None:
        res = await self._session.execute(
            self._base(user_id).where(Transaction.id == transaction_id)
        )
        return res.scalar_one_or_none()

    async def create(self, tx: Transaction) -> Transaction:
        self._session.add(tx)
        await self._session.flush()
        return tx

    async def list(
        self,
        *,
        user_id: str,
        q: str | None,
        account_id: str | None,
        category_id: str | None,
        type: str | None,
        start: datetime | None,
        end: datetime | None,
        sort: str,
        limit: int,
        offset: int,
    ) -> tuple[list[Transaction], int]:
        stmt = self._base(user_id)

        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                sa.or_(Transaction.note.ilike(like), Transaction.merchant.ilike(like))
            )
        if account_id:
            stmt = stmt.where(Transaction.account_id == account_id)
        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)
        if type:
            stmt = stmt.where(Transaction.type == type)
        if start:
            stmt = stmt.where(Transaction.occurred_at >= start)
        if end:
            stmt = stmt.where(Transaction.occurred_at < end)

        if sort == "occurred_at_asc":
            stmt = stmt.order_by(Transaction.occurred_at.asc(), Transaction.created_at.asc())
        else:
            stmt = stmt.order_by(Transaction.occurred_at.desc(), Transaction.created_at.desc())

        total_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self._session.execute(total_stmt)
        total = int(total_res.scalar_one())

        res = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(res.scalars().all()), total

    async def soft_delete(self, user_id: str, transaction_id: str) -> None:
        await self._session.execute(
            update(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.id == transaction_id,
                Transaction.deleted_at.is_(None),
            )
            .values(deleted_at=sa.func.now())
        )
