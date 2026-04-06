from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.core.responses import Page, PageMeta
from app.schemas.account import AccountCreateRequest, AccountResponse, AccountUpdateRequest
from app.services.account_service import AccountService

router = APIRouter()


def _to_response(a) -> AccountResponse:
    return AccountResponse(
        id=a.id,
        name=a.name,
        type=a.type,
        currency=a.currency,
        balance=a.balance,
        archived=a.archived,
        allow_transactions_when_archived=a.allow_transactions_when_archived,
    )


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an account",
    description="Creates a new account (wallet/bank/card/etc.) for the current user.",
)
async def create_account(
    payload: AccountCreateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> AccountResponse:
    a = await AccountService(session).create(
        user=user,
        name=payload.name,
        type=payload.type,
        currency=payload.currency,
        initial_balance=payload.initial_balance,
        archived=payload.archived,
        allow_transactions_when_archived=payload.allow_transactions_when_archived,
    )
    return _to_response(a)


@router.get("", response_model=Page[AccountResponse], summary="List accounts (paginated)")
async def list_accounts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> Page[AccountResponse]:
    items, total = await AccountService(session).list_paginated(
        user=user, limit=limit, offset=offset
    )
    return Page(
        items=[_to_response(a) for a in items],
        meta=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get account details",
    description="Returns a single account owned by the current user.",
)
async def get_account(
    account_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> AccountResponse:
    a = await AccountService(session).get(user=user, account_id=account_id)
    return _to_response(a)


@router.patch(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update an account",
    description="Updates mutable account fields (name, archived flags).",
)
async def update_account(
    account_id: str,
    payload: AccountUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> AccountResponse:
    a = await AccountService(session).update(
        user=user,
        account_id=account_id,
        name=payload.name,
        archived=payload.archived,
        allow_transactions_when_archived=payload.allow_transactions_when_archived,
    )
    return _to_response(a)


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an account",
    description="Soft-deletes an account owned by the current user.",
)
async def delete_account(
    account_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> None:
    await AccountService(session).delete(user=user, account_id=account_id)
