from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.enums import ThemePreference
from app.models.setting import Setting
from app.models.user import User
from app.repositories.setting_repository import SettingRepository


class SettingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = SettingRepository(session)

    async def get_me(self, *, user: User) -> Setting:
        s = await self._settings.get_by_user_id(user.id)
        if s is None:
            raise NotFoundError("Settings not found")
        return s

    async def update_me(
        self,
        *,
        user: User,
        preferred_currency: str | None,
        locale: str | None,
        timezone: str | None,
        notifications_enabled: bool | None,
        budget_alerts_enabled: bool | None,
        theme_preference: ThemePreference | None,
    ) -> Setting:
        s = await self.get_me(user=user)
        if preferred_currency is not None:
            s.preferred_currency = preferred_currency.upper()
        if locale is not None:
            s.locale = locale
        if timezone is not None:
            s.timezone = timezone
        if notifications_enabled is not None:
            s.notifications_enabled = notifications_enabled
        if budget_alerts_enabled is not None:
            s.budget_alerts_enabled = budget_alerts_enabled
        if theme_preference is not None:
            s.theme_preference = theme_preference.value
        await self._session.commit()
        await self._session.refresh(s)
        return s
