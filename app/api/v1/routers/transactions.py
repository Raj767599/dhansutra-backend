from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.core.responses import Page, PageMeta
from app.domain.enums import TransactionType
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionListItem,
    TransactionOverviewResponse,
    TransactionResponse,
    TransactionUpdateRequest,
)
from app.services.transaction_service import TransactionService

router = APIRouter()


def _to_response(tx) -> TransactionResponse:
    return TransactionResponse(
        id=tx.id,
        type=TransactionType(tx.type),
        amount=tx.amount,
        currency=tx.currency,
        occurred_at=tx.occurred_at,
        note=tx.note,
        merchant=tx.merchant,
        account_id=tx.account_id,
        destination_account_id=tx.destination_account_id,
        category_id=tx.category_id,
    )


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transaction",
    description="Creates an income/expense/transfer transaction and applies balance rules server-side.",
)
async def create_transaction(
    payload: TransactionCreateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> TransactionResponse:
    tx = await TransactionService(session).create(
        user=user,
        type=payload.type,
        amount=payload.amount,
        occurred_at=payload.occurred_at,
        account_id=payload.account_id,
        category_id=payload.category_id,
        destination_account_id=payload.destination_account_id,
        note=payload.note,
        merchant=payload.merchant,
        recurring_template=payload.recurring_template,
    )
    return _to_response(tx)


@router.get(
    "",
    response_model=Page[TransactionListItem],
    summary="List transactions (filters + pagination)",
    description="Lists transactions for the current user with search, filters, sorting, and pagination.",
)
async def list_transactions(
    q: str | None = Query(default=None),
    account_id: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    type: TransactionType | None = Query(default=None),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    sort: str = Query(default="occurred_at_desc", pattern="^(occurred_at_desc|occurred_at_asc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> Page[TransactionListItem]:
    items, total = await TransactionService(session).list(
        user=user,
        q=q,
        account_id=account_id,
        category_id=category_id,
        type=type,
        start=start,
        end=end,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[TransactionListItem(**_to_response(t).model_dump()) for t in items],
        meta=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction details",
    description="Returns a single transaction owned by the current user.",
)
async def get_transaction(
    transaction_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> TransactionResponse:
    tx = await TransactionService(session).get(user=user, transaction_id=transaction_id)
    return _to_response(tx)


@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update a transaction",
    description="Updates mutable transaction fields and safely reverses/reapplies balance impacts.",
)
async def update_transaction(
    transaction_id: str,
    payload: TransactionUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> TransactionResponse:
    tx = await TransactionService(session).update(
        user=user,
        transaction_id=transaction_id,
        amount=payload.amount,
        occurred_at=payload.occurred_at,
        account_id=payload.account_id,
        category_id=payload.category_id,
        destination_account_id=payload.destination_account_id,
        note=payload.note,
        merchant=payload.merchant,
        recurring_template=payload.recurring_template,
    )
    return _to_response(tx)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
    description="Soft-deletes the transaction and reverses its balance impact.",
)
async def delete_transaction(
    transaction_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> None:
    await TransactionService(session).delete(user=user, transaction_id=transaction_id)


@router.get(
    "/summary/overview",
    response_model=TransactionOverviewResponse,
    summary="Transaction totals overview",
    description="Returns totals (income/expense/transfers/net cashflow) for an optional date range.",
)
async def overview(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> TransactionOverviewResponse:
    data = await TransactionService(session).overview(user=user, start=start, end=end)
    return TransactionOverviewResponse(**data)  # type: ignore[arg-type]
