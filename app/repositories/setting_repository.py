from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.setting import Setting


class SettingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: str) -> Setting | None:
        res = await self._session.execute(
            select(Setting).where(Setting.user_id == user_id, Setting.deleted_at.is_(None))
        )
        return res.scalar_one_or_none()
