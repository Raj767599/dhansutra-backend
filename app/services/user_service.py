from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def get_me(self, *, user: User) -> User:
        return user

    async def update_me(
        self, *, user: User, full_name: str | None = None, onboarding_completed: bool | None = None
    ) -> User:
        if full_name is not None:
            user.full_name = full_name
        if onboarding_completed is not None:
            user.onboarding_completed = onboarding_completed
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def change_password(
        self, *, user: User, current_password: str, new_password: str
    ) -> None:
        if not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        user.password_hash = hash_password(new_password)
        user.token_version += 1  # revoke existing access tokens
        await self._session.commit()
