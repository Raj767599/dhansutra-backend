from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.core.responses import Page, PageMeta
from app.schemas.budget import BudgetCreateRequest, BudgetResponse, BudgetUpdateRequest
from app.services.budget_service import BudgetService

router = APIRouter()


def _to_response(row: dict) -> BudgetResponse:
    b = row["budget"]
    return BudgetResponse(
        id=b.id,
        year=b.year,
        month=b.month,
        amount=b.amount,
        currency=b.currency,
        category_id=b.category_id,
        spent=row["spent"],
        remaining=row["remaining"],
        usage_pct=row["usage_pct"],
        is_over_budget=row["is_over_budget"],
    )


@router.post(
    "",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a monthly budget",
    description="Creates a monthly budget; optionally scoped to an expense category.",
)
async def create_budget(
    payload: BudgetCreateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> BudgetResponse:
    b = await BudgetService(session).create(
        user=user,
        year=payload.year,
        month=payload.month,
        amount=payload.amount,
        currency=payload.currency,
        category_id=payload.category_id,
    )
    row = await BudgetService(session).get(user=user, budget_id=b.id)
    return _to_response(row)


@router.get("", response_model=Page[BudgetResponse], summary="List budgets (paginated)")
async def list_budgets(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> Page[BudgetResponse]:
    items, total = await BudgetService(session).list_paginated(
        user=user, limit=limit, offset=offset
    )
    return Page(
        items=[_to_response(r) for r in items],
        meta=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
    summary="Get budget details",
    description="Returns a budget with calculated spent/remaining/usage fields.",
)
async def get_budget(
    budget_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> BudgetResponse:
    row = await BudgetService(session).get(user=user, budget_id=budget_id)
    return _to_response(row)


@router.patch(
    "/{budget_id}",
    response_model=BudgetResponse,
    summary="Update a budget",
    description="Updates budget amount. Calculated fields are returned in the response.",
)
async def update_budget(
    budget_id: str,
    payload: BudgetUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> BudgetResponse:
    await BudgetService(session).update(user=user, budget_id=budget_id, amount=payload.amount)
    row = await BudgetService(session).get(user=user, budget_id=budget_id)
    return _to_response(row)


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a budget",
    description="Soft-deletes a budget owned by the current user.",
)
async def delete_budget(
    budget_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> None:
    await BudgetService(session).delete(user=user, budget_id=budget_id)
