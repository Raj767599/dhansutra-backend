from __future__ import annotations

import builtins

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.enums import CategoryType
from app.models.category import Category
from app.models.user import User
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._categories = CategoryRepository(session)

    async def list(self, *, user: User, type: CategoryType | None) -> builtins.list[Category]:
        return await self._categories.list(user.id, type.value if type else None)

    async def list_paginated(
        self, *, user: User, type: CategoryType | None, limit: int, offset: int
    ) -> tuple[builtins.list[Category], int]:
        return await self._categories.list_paginated(
            user_id=user.id, type=type.value if type else None, limit=limit, offset=offset
        )

    async def get(self, *, user: User, category_id: str) -> Category:
        cat = await self._categories.get(user.id, category_id)
        if cat is None:
            raise NotFoundError("Category not found")
        return cat

    async def create(
        self, *, user: User, name: str, type: CategoryType, icon: str | None, color: str | None
    ) -> Category:
        cat = Category(
            user_id=user.id,
            name=name,
            type=type.value,
            icon=icon,
            color=color,
            is_system=False,
        )
        await self._categories.create(cat)
        await self._session.commit()
        return cat

    async def update(
        self,
        *,
        user: User,
        category_id: str,
        name: str | None,
        icon: str | None,
        color: str | None,
    ) -> Category:
        cat = await self.get(user=user, category_id=category_id)
        if cat.is_system:
            raise ForbiddenError("System categories cannot be modified")
        if cat.user_id != user.id:
            raise ForbiddenError()
        if name is not None:
            cat.name = name
        if icon is not None:
            cat.icon = icon
        if color is not None:
            cat.color = color
        await self._session.commit()
        await self._session.refresh(cat)
        return cat

    async def delete(self, *, user: User, category_id: str) -> None:
        cat = await self.get(user=user, category_id=category_id)
        if cat.is_system:
            raise ForbiddenError("System categories cannot be deleted")
        await self._categories.soft_delete(user.id, category_id)
        await self._session.commit()
