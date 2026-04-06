from __future__ import annotations

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import current_user, db_session_from_request
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserMeResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserMeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a user and default settings. Does not issue tokens; call /auth/login next.",
)
async def register(
    payload: RegisterRequest, session: AsyncSession = Depends(db_session_from_request)
) -> UserMeResponse:
    user = await AuthService(session).register(
        email=payload.email, password=payload.password, full_name=payload.full_name
    )
    await session.commit()
    return UserMeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        onboarding_completed=user.onboarding_completed,
    )


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login and obtain access/refresh tokens",
    description="Returns a JWT access token and an opaque refresh token (stored hashed server-side).",
)
async def login(
    payload: LoginRequest, session: AsyncSession = Depends(db_session_from_request)
) -> TokenPair:
    access, refresh = await AuthService(session).login(
        email=payload.email, password=payload.password
    )
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Refresh access token (rotating refresh token)",
    description="Rotates refresh token: old token is revoked and a new refresh token is issued.",
)
async def refresh(
    payload: RefreshRequest, session: AsyncSession = Depends(db_session_from_request)
) -> TokenPair:
    access, refresh_token = await AuthService(session).refresh(refresh_token=payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (revoke refresh token)",
    description="Revokes the provided refresh token. Idempotent if token is unknown or already revoked.",
)
async def logout(
    payload: LogoutRequest, session: AsyncSession = Depends(db_session_from_request)
) -> None:
    await AuthService(session).logout(refresh_token=payload.refresh_token)


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user (from access token)",
    description="Validates JWT access token and returns the current user's public profile.",
)
async def me(user=Security(current_user)) -> UserMeResponse:
    return UserMeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        onboarding_completed=user.onboarding_completed,
    )
