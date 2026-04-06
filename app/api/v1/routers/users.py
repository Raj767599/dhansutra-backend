from __future__ import annotations

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.schemas.user import ChangePasswordRequest, UserMeResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get my profile",
    description="Returns the current user's public profile data.",
)
async def get_me(user=Security(current_user)) -> UserMeResponse:
    return UserMeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        onboarding_completed=user.onboarding_completed,
    )


@router.patch(
    "/me",
    response_model=UserMeResponse,
    summary="Update my profile",
    description="Updates profile fields (full_name, onboarding_completed).",
)
async def update_me(
    payload: UserUpdateRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> UserMeResponse:
    u = await UserService(session).update_me(
        user=user, full_name=payload.full_name, onboarding_completed=payload.onboarding_completed
    )
    return UserMeResponse(
        id=u.id, email=u.email, full_name=u.full_name, onboarding_completed=u.onboarding_completed
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change my password",
    description="Changes password after verifying current password. Revokes existing access tokens.",
)
async def change_password(
    payload: ChangePasswordRequest,
    session: AsyncSession = Depends(db_session_from_request),
    user=Security(current_user),
) -> None:
    await UserService(session).change_password(
        user=user, current_password=payload.current_password, new_password=payload.new_password
    )
