from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import ThemePreference


class SettingResponse(BaseModel):
    preferred_currency: str
    locale: str
    timezone: str
    notifications_enabled: bool
    budget_alerts_enabled: bool
    theme_preference: ThemePreference


class SettingUpdateRequest(BaseModel):
    preferred_currency: str | None = Field(default=None, min_length=3, max_length=3)
    locale: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=64)
    notifications_enabled: bool | None = None
    budget_alerts_enabled: bool | None = None
    theme_preference: ThemePreference | None = None
