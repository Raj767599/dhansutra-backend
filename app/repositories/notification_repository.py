from __future__ import annotations

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base(self, user_id: str) -> Select[tuple[Notification]]:
        return select(Notification).where(
            Notification.user_id == user_id, Notification.deleted_at.is_(None)
        )

    async def list(self, user_id: str, *, unread_only: bool = False) -> list[Notification]:
        stmt = self._base(user_id)
        if unread_only:
            stmt = stmt.where(Notification.read.is_(False))
        res = await self._session.execute(stmt.order_by(Notification.created_at.desc()))
        return list(res.scalars().all())

    async def create(self, n: Notification) -> Notification:
        self._session.add(n)
        await self._session.flush()
        return n

    async def mark_read(self, user_id: str, notification_id: str) -> None:
        await self._session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.id == notification_id,
                Notification.deleted_at.is_(None),
            )
            .values(read=True)
        )
