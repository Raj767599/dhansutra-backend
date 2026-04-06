from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        res = await self._session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        res = await self._session.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user

    async def update_token_version(self, user_id: str, new_version: int) -> None:
        await self._session.execute(
            update(User).where(User.id == user_id).values(token_version=new_version)
        )
