from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import NotificationType
from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = NotificationRepository(session)

    async def list(self, *, user: User, unread_only: bool = False) -> list[Notification]:
        return await self._repo.list(user.id, unread_only=unread_only)

    async def create(
        self,
        *,
        user: User,
        type: NotificationType,
        title: str,
        body: str,
        scheduled_for: datetime | None,
    ) -> Notification:
        n = Notification(
            user_id=user.id,
            type=type.value,
            title=title,
            body=body,
            scheduled_for=scheduled_for,
            read=False,
        )
        await self._repo.create(n)
        await self._session.commit()
        return n
