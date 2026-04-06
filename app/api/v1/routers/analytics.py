from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.schemas.analytics import (
    CashflowResponse,
    MonthlyTrendResponse,
    SpendingByCategoryResponse,
    TopCategoriesResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "/spending-by-category",
    response_model=SpendingByCategoryResponse,
    summary="Spending by category",
    description="Aggregates expense totals by category for an optional date range.",
)
async def spending_by_category(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> SpendingByCategoryResponse:
    data = await AnalyticsService(session).spending_by_category(user=user, start=start, end=end)
    return SpendingByCategoryResponse(**data)


@router.get(
    "/monthly-trend",
    response_model=MonthlyTrendResponse,
    summary="Monthly trend",
    description="Aggregates monthly income/expense/net trend for the last N months.",
)
async def monthly_trend(
    months: int = Query(default=12, ge=1, le=36),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> MonthlyTrendResponse:
    data = await AnalyticsService(session).monthly_trend(user=user, months=months)
    return MonthlyTrendResponse(**data)


@router.get(
    "/cashflow",
    response_model=CashflowResponse,
    summary="Cashflow",
    description="Returns income, expense, and net cashflow for an optional date range.",
)
async def cashflow(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> CashflowResponse:
    data = await AnalyticsService(session).cashflow(user=user, start=start, end=end)
    return CashflowResponse(**data)


@router.get(
    "/top-categories",
    response_model=TopCategoriesResponse,
    summary="Top spending categories",
    description="Returns top expense categories by total spent for an optional date range.",
)
async def top_categories(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
    limit: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> TopCategoriesResponse:
    data = await AnalyticsService(session).top_categories(
        user=user, start=start, end=end, limit=limit
    )
    return TopCategoriesResponse(**data)
