from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.core.responses import Page, PageMeta
from app.domain.enums import CategoryType
from app.schemas.category import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest
from app.services.category_service import CategoryService

router = APIRouter()


def _to_response(c) -> CategoryResponse:
    return CategoryResponse(
        id=c.id,
        name=c.name,
        type=c.type,
        icon=c.icon,
        color=c.color,
        is_system=c.is_system,
    )


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
    description="Creates a custom category for the current user.",
)
async def create_category(
    payload: CategoryCreateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> CategoryResponse:
    c = await CategoryService(session).create(
        user=user, name=payload.name, type=payload.type, icon=payload.icon, color=payload.color
    )
    return _to_response(c)


@router.get("", response_model=Page[CategoryResponse], summary="List categories (paginated)")
async def list_categories(
    type: CategoryType | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> Page[CategoryResponse]:
    items, total = await CategoryService(session).list_paginated(
        user=user, type=type, limit=limit, offset=offset
    )
    return Page(
        items=[_to_response(c) for c in items],
        meta=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category details",
    description="Returns a system category or a user-owned custom category.",
)
async def get_category(
    category_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> CategoryResponse:
    c = await CategoryService(session).get(user=user, category_id=category_id)
    return _to_response(c)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
    description="Updates a user-owned category. System categories cannot be modified.",
)
async def update_category(
    category_id: str,
    payload: CategoryUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> CategoryResponse:
    c = await CategoryService(session).update(
        user=user,
        category_id=category_id,
        name=payload.name,
        icon=payload.icon,
        color=payload.color,
    )
    return _to_response(c)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    description="Soft-deletes a user-owned category. System categories cannot be deleted.",
)
async def delete_category(
    category_id: str,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> None:
    await CategoryService(session).delete(user=user, category_id=category_id)
