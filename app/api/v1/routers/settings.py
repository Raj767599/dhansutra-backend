from __future__ import annotations

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.domain.enums import ThemePreference
from app.schemas.setting import SettingResponse, SettingUpdateRequest
from app.services.setting_service import SettingService

router = APIRouter()


def _to_response(s) -> SettingResponse:
    return SettingResponse(
        preferred_currency=s.preferred_currency,
        locale=s.locale,
        timezone=s.timezone,
        notifications_enabled=s.notifications_enabled,
        budget_alerts_enabled=s.budget_alerts_enabled,
        theme_preference=ThemePreference(s.theme_preference),
    )


@router.get(
    "/me",
    response_model=SettingResponse,
    summary="Get my settings",
    description="Returns the current user's preferences (currency, locale, notifications, theme).",
)
async def get_settings(
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> SettingResponse:
    s = await SettingService(session).get_me(user=user)
    return _to_response(s)


@router.patch(
    "/me",
    response_model=SettingResponse,
    summary="Update my settings",
    description="Updates the current user's preferences (partial update).",
)
async def update_settings(
    payload: SettingUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> SettingResponse:
    s = await SettingService(session).update_me(
        user=user,
        preferred_currency=payload.preferred_currency,
        locale=payload.locale,
        timezone=payload.timezone,
        notifications_enabled=payload.notifications_enabled,
        budget_alerts_enabled=payload.budget_alerts_enabled,
        theme_preference=payload.theme_preference,
    )
    return _to_response(s)
