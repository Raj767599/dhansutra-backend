from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.core.responses import Page, PageMeta
from app.schemas.savings_goal import (
    GoalContributionCreateRequest,
    GoalContributionResponse,
    SavingsGoalCreateRequest,
    SavingsGoalResponse,
    SavingsGoalUpdateRequest,
)
from app.services.savings_goal_service import SavingsGoalService

router = APIRouter()


def _contrib_resp(c) -> GoalContributionResponse:
    return GoalContributionResponse(
        id=c.id, amount=c.amount, contributed_at=c.contributed_at, note=c.note
    )


def _goal_resp(g, contrib) -> SavingsGoalResponse:
    progress = (
        (g.current_amount / g.target_amount * Decimal("100")).quantize(Decimal("0.01"))
        if g.target_amount > 0
        else Decimal("0")
    )
    return SavingsGoalResponse(
        id=g.id,
        name=g.name,
        target_amount=g.target_amount,
        current_amount=g.current_amount,
        currency=g.currency,
        deadline=g.deadline,
        completed=g.completed,
        progress_pct=progress,
        contributions=[_contrib_resp(c) for c in contrib],
    )


@router.post(
    "",
    response_model=SavingsGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a savings goal",
    description="Creates a savings goal for the current user.",
)
async def create_goal(
    payload: SavingsGoalCreateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> SavingsGoalResponse:
    s = SavingsGoalService(session)
    g = await s.create(
        user=user,
        name=payload.name,
        target_amount=payload.target_amount,
        currency=payload.currency,
        deadline=payload.deadline,
    )
    goal, contrib = await s.get_with_contributions(user=user, goal_id=g.id)
    return _goal_resp(goal, contrib)


@router.get("", response_model=Page[SavingsGoalResponse], summary="List goals (paginated)")
async def list_goals(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> Page[SavingsGoalResponse]:
    s = SavingsGoalService(session)
    items, total = await s.list_with_contributions_paginated(user=user, limit=limit, offset=offset)
    return Page(
        items=[_goal_resp(g, c) for (g, c) in items],
        meta=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get(
    "/{goal_id}",
    response_model=SavingsGoalResponse,
    summary="Get goal details",
    description="Returns a goal including its contributions list.",
)
async def get_goal(
    goal_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> SavingsGoalResponse:
    s = SavingsGoalService(session)
    g, contrib = await s.get_with_contributions(user=user, goal_id=goal_id)
    return _goal_resp(g, contrib)


@router.patch(
    "/{goal_id}",
    response_model=SavingsGoalResponse,
    summary="Update a savings goal",
    description="Updates goal fields (name, target_amount, deadline, completed).",
)
async def update_goal(
    goal_id: str,
    payload: SavingsGoalUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> SavingsGoalResponse:
    s = SavingsGoalService(session)
    await s.update(
        user=user,
        goal_id=goal_id,
        name=payload.name,
        target_amount=payload.target_amount,
        deadline=payload.deadline,
        completed=payload.completed,
    )
    g, contrib = await s.get_with_contributions(user=user, goal_id=goal_id)
    return _goal_resp(g, contrib)


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a savings goal",
    description="Soft-deletes a goal owned by the current user.",
)
async def delete_goal(
    goal_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> None:
    await SavingsGoalService(session).delete(user=user, goal_id=goal_id)


@router.post(
    "/{goal_id}/contributions",
    response_model=GoalContributionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a goal contribution",
    description="Adds a contribution and updates goal progress/current_amount.",
)
async def add_contribution(
    goal_id: str,
    payload: GoalContributionCreateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> GoalContributionResponse:
    c = await SavingsGoalService(session).add_contribution(
        user=user,
        goal_id=goal_id,
        amount=payload.amount,
        contributed_at=payload.contributed_at,
        note=payload.note,
    )
    return _contrib_resp(c)
