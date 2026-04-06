from __future__ import annotations

import builtins

import sqlalchemy as sa
from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_for_user(self, user_id: str) -> Select[tuple[Category]]:
        # user can see system categories + own categories
        return select(Category).where(
            Category.deleted_at.is_(None),
            sa.or_(Category.is_system.is_(True), Category.user_id == user_id),
        )

    async def list(self, user_id: str, type: str | None = None) -> builtins.list[Category]:
        stmt = self._base_for_user(user_id)
        if type is not None:
            stmt = stmt.where(Category.type == type)
        res = await self._session.execute(
            stmt.order_by(Category.is_system.desc(), Category.name.asc())
        )
        return list(res.scalars().all())

    async def list_paginated(
        self, *, user_id: str, type: str | None, limit: int, offset: int
    ) -> tuple[builtins.list[Category], int]:
        stmt = self._base_for_user(user_id)
        if type is not None:
            stmt = stmt.where(Category.type == type)
        stmt = stmt.order_by(Category.is_system.desc(), Category.name.asc())
        total_res = await self._session.execute(select(func.count()).select_from(stmt.subquery()))
        total = int(total_res.scalar_one())
        res = await self._session.execute(stmt.limit(limit).offset(offset))
        return list(res.scalars().all()), total

    async def get(self, user_id: str, category_id: str) -> Category | None:
        res = await self._session.execute(
            self._base_for_user(user_id).where(Category.id == category_id)
        )
        return res.scalar_one_or_none()

    async def create(self, category: Category) -> Category:
        self._session.add(category)
        await self._session.flush()
        return category

    async def soft_delete(self, user_id: str, category_id: str) -> None:
        # only allow deleting user-owned categories
        await self._session.execute(
            update(Category)
            .where(
                Category.id == category_id,
                Category.user_id == user_id,
                Category.is_system.is_(False),
                Category.deleted_at.is_(None),
            )
            .values(deleted_at=sa.func.now())
        )
