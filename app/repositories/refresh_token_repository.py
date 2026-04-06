from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        await self._session.flush()
        return token

    async def get_active_by_hash(self, token_hash: str) -> RefreshToken | None:
        now = datetime.now(timezone.utc)
        res = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
                RefreshToken.deleted_at.is_(None),
            )
        )
        return res.scalar_one_or_none()

    async def revoke_by_id(self, token_id: str) -> None:
        await self._session.execute(
            update(RefreshToken).where(RefreshToken.id == token_id).values(revoked=True)
        )

    async def revoke_all_for_user(self, user_id: str) -> None:
        await self._session.execute(
            update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        )
