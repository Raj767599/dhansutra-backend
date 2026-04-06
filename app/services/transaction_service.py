from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationAppError
from app.domain.enums import CategoryType, TransactionType
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.utils.datetime import utc_now


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._tx = TransactionRepository(session)
        self._accounts = AccountRepository(session)
        self._categories = CategoryRepository(session)

    async def _account(self, *, user: User, account_id: str) -> Account:
        a = await self._accounts.get(user.id, account_id)
        if a is None:
            raise NotFoundError("Account not found")
        return a

    async def _category(self, *, user: User, category_id: str) -> Category:
        c = await self._categories.get(user.id, category_id)
        if c is None:
            raise NotFoundError("Category not found")
        return c

    def _impact(self, *, tx_type: TransactionType, amount: Decimal) -> tuple[Decimal, Decimal]:
        if tx_type == TransactionType.income:
            return (amount, Decimal("0"))
        if tx_type == TransactionType.expense:
            return (-amount, Decimal("0"))
        return (-amount, amount)  # transfer: (source_delta, dest_delta)

    async def _apply(
        self, *, source: Account, dest: Account | None, source_delta: Decimal, dest_delta: Decimal
    ) -> None:
        new_source = (source.balance or Decimal("0")) + source_delta
        if new_source < 0:
            raise ValidationAppError("Insufficient funds", details={"account_id": source.id})
        source.balance = new_source
        if dest is not None:
            new_dest = (dest.balance or Decimal("0")) + dest_delta
            if new_dest < 0:
                raise ValidationAppError(
                    "Invalid destination balance", details={"destination_account_id": dest.id}
                )
            dest.balance = new_dest

    async def create(
        self,
        *,
        user: User,
        type: TransactionType,
        amount: Decimal,
        occurred_at: datetime,
        account_id: str,
        category_id: str | None,
        destination_account_id: str | None,
        note: str | None,
        merchant: str | None,
        recurring_template: str | None,
    ) -> Transaction:
        source = await self._account(user=user, account_id=account_id)
        if source.archived and not source.allow_transactions_when_archived:
            raise ForbiddenError("Archived account cannot accept new transactions")

        dest: Account | None = None
        if type == TransactionType.transfer:
            if not destination_account_id:
                raise ValidationAppError(
                    details={"destination_account_id": "Required for transfer"}
                )
            if destination_account_id == account_id:
                raise ValidationAppError(
                    details={"destination_account_id": "Must differ from account_id"}
                )
            dest = await self._account(user=user, account_id=destination_account_id)
            if dest.archived and not dest.allow_transactions_when_archived:
                raise ForbiddenError("Archived destination account cannot accept transfers")
            if dest.currency.upper() != source.currency.upper():
                raise ValidationAppError(
                    "Transfer currency mismatch", details={"currency": "Accounts must match"}
                )
            if category_id is not None:
                raise ValidationAppError(details={"category_id": "Not allowed for transfer"})
        else:
            if category_id is None:
                raise ValidationAppError(details={"category_id": "Required for income/expense"})
            cat = await self._category(user=user, category_id=category_id)
            expected = (
                CategoryType.income if type == TransactionType.income else CategoryType.expense
            )
            if CategoryType(cat.type) != expected:
                raise ValidationAppError(
                    "Category type mismatch", details={"category_id": f"Must be {expected.value}"}
                )

        sd, dd = self._impact(tx_type=type, amount=amount)
        await self._apply(source=source, dest=dest, source_delta=sd, dest_delta=dd)

        tx = Transaction(
            user_id=user.id,
            type=type.value,
            amount=amount,
            currency=source.currency.upper(),
            occurred_at=occurred_at.astimezone(timezone.utc),
            note=note,
            merchant=merchant,
            account_id=source.id,
            destination_account_id=dest.id if dest else None,
            category_id=category_id if type != TransactionType.transfer else None,
            recurring_template=recurring_template,
        )
        await self._tx.create(tx)
        await self._session.commit()
        return tx

    async def get(self, *, user: User, transaction_id: str) -> Transaction:
        tx = await self._tx.get(user.id, transaction_id)
        if tx is None:
            raise NotFoundError("Transaction not found")
        return tx

    async def list(
        self,
        *,
        user: User,
        q: str | None,
        account_id: str | None,
        category_id: str | None,
        type: TransactionType | None,
        start: datetime | None,
        end: datetime | None,
        sort: str,
        limit: int,
        offset: int,
    ) -> tuple[list[Transaction], int]:
        return await self._tx.list(
            user_id=user.id,
            q=q,
            account_id=account_id,
            category_id=category_id,
            type=type.value if type else None,
            start=start,
            end=end,
            sort=sort,
            limit=limit,
            offset=offset,
        )

    async def update(
        self,
        *,
        user: User,
        transaction_id: str,
        amount: Decimal | None,
        occurred_at: datetime | None,
        account_id: str | None,
        category_id: str | None,
        destination_account_id: str | None,
        note: str | None,
        merchant: str | None,
        recurring_template: str | None,
    ) -> Transaction:
        tx = await self.get(user=user, transaction_id=transaction_id)
        tx_type = TransactionType(tx.type)

        old_source = await self._account(user=user, account_id=tx.account_id)
        old_dest = (
            await self._account(user=user, account_id=tx.destination_account_id)
            if tx.destination_account_id
            else None
        )
        old_sd, old_dd = self._impact(tx_type=tx_type, amount=tx.amount)
        await self._apply(
            source=old_source, dest=old_dest, source_delta=-old_sd, dest_delta=-old_dd
        )

        new_amount = amount if amount is not None else tx.amount
        new_occurred_at = occurred_at.astimezone(timezone.utc) if occurred_at else tx.occurred_at
        new_source_id = account_id if account_id else tx.account_id
        new_dest_id = (
            destination_account_id
            if destination_account_id is not None
            else tx.destination_account_id
        )
        new_cat_id = category_id if category_id is not None else tx.category_id

        new_source = await self._account(user=user, account_id=new_source_id)
        if new_source.archived and not new_source.allow_transactions_when_archived:
            raise ForbiddenError("Archived account cannot accept new transactions")

        new_dest: Account | None = None
        if tx_type == TransactionType.transfer:
            if not new_dest_id:
                raise ValidationAppError(
                    details={"destination_account_id": "Required for transfer"}
                )
            if new_dest_id == new_source_id:
                raise ValidationAppError(
                    details={"destination_account_id": "Must differ from account_id"}
                )
            new_dest = await self._account(user=user, account_id=new_dest_id)
            if new_dest.archived and not new_dest.allow_transactions_when_archived:
                raise ForbiddenError("Archived destination account cannot accept transfers")
            if new_dest.currency.upper() != new_source.currency.upper():
                raise ValidationAppError(
                    "Transfer currency mismatch", details={"currency": "Accounts must match"}
                )
            new_cat_id = None
        else:
            if new_cat_id is None:
                raise ValidationAppError(details={"category_id": "Required for income/expense"})
            cat = await self._category(user=user, category_id=new_cat_id)
            expected = (
                CategoryType.income if tx_type == TransactionType.income else CategoryType.expense
            )
            if CategoryType(cat.type) != expected:
                raise ValidationAppError(
                    "Category type mismatch", details={"category_id": f"Must be {expected.value}"}
                )

        new_sd, new_dd = self._impact(tx_type=tx_type, amount=new_amount)
        await self._apply(source=new_source, dest=new_dest, source_delta=new_sd, dest_delta=new_dd)

        tx.amount = new_amount
        tx.occurred_at = new_occurred_at
        tx.account_id = new_source.id
        tx.destination_account_id = new_dest.id if new_dest else None
        tx.currency = new_source.currency.upper()
        tx.category_id = new_cat_id
        if note is not None:
            tx.note = note
        if merchant is not None:
            tx.merchant = merchant
        if recurring_template is not None:
            tx.recurring_template = recurring_template

        await self._session.commit()
        await self._session.refresh(tx)
        return tx

    async def delete(self, *, user: User, transaction_id: str) -> None:
        tx = await self.get(user=user, transaction_id=transaction_id)
        tx_type = TransactionType(tx.type)

        source = await self._account(user=user, account_id=tx.account_id)
        dest = (
            await self._account(user=user, account_id=tx.destination_account_id)
            if tx.destination_account_id
            else None
        )
        sd, dd = self._impact(tx_type=tx_type, amount=tx.amount)
        await self._apply(source=source, dest=dest, source_delta=-sd, dest_delta=-dd)

        await self._tx.soft_delete(user.id, transaction_id)
        await self._session.commit()

    async def overview(
        self, *, user: User, start: datetime | None, end: datetime | None
    ) -> dict[str, Decimal | datetime]:
        start_dt = start or datetime(1970, 1, 1, tzinfo=timezone.utc)
        end_dt = end or utc_now()

        t = Transaction
        base = sa.and_(
            t.user_id == user.id,
            t.deleted_at.is_(None),
            t.occurred_at >= start_dt,
            t.occurred_at < end_dt,
        )

        total_income = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.income.value
            )
        )
        total_expense = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.expense.value
            )
        )
        transfer_out = await self._session.execute(
            select(func.coalesce(func.sum(t.amount), 0)).where(
                base, t.type == TransactionType.transfer.value
            )
        )
        # transfer_in == transfer_out for same currency; keep both for UI symmetry
        inc = Decimal(str(total_income.scalar_one()))
        exp = Decimal(str(total_expense.scalar_one()))
        tr = Decimal(str(transfer_out.scalar_one()))
        return {
            "start": start_dt,
            "end": end_dt,
            "total_income": inc,
            "total_expense": exp,
            "total_transfer_out": tr,
            "total_transfer_in": tr,
            "net_cashflow": inc - exp,
        }
