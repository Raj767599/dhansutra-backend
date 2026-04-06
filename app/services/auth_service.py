from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    sha256_hex,
    verify_password,
)
from app.domain.constants import DEFAULT_CURRENCY
from app.models.refresh_token import RefreshToken
from app.models.setting import Setting
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._refresh = RefreshTokenRepository(session)

    async def register(self, *, email: str, password: str, full_name: str | None) -> User:
        existing = await self._users.get_by_email(email)
        if existing is not None and existing.deleted_at is None:
            raise ConflictError("Email already registered")

        user = User(email=email.lower(), password_hash=hash_password(password), full_name=full_name)
        await self._users.create(user)

        # create default settings record
        setting = Setting(
            user_id=user.id,
            preferred_currency=DEFAULT_CURRENCY,
            locale="en-US",
            timezone="UTC",
            notifications_enabled=True,
            budget_alerts_enabled=True,
            theme_preference="system",
        )
        self._session.add(setting)
        await self._session.flush()
        return user

    async def login(self, *, email: str, password: str) -> tuple[str, str]:
        user = await self._users.get_by_email(email.lower())
        if user is None or user.deleted_at is not None:
            raise UnauthorizedError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")

        access = create_access_token(subject=user.id, token_version=user.token_version)
        refresh_token, expires_at = create_refresh_token(
            subject=user.id, token_version=user.token_version
        )
        token_row = RefreshToken(
            user_id=user.id,
            token_hash=sha256_hex(refresh_token),
            expires_at=expires_at,
            revoked=False,
        )
        await self._refresh.create(token_row)
        await self._session.commit()
        return access, refresh_token

    async def refresh(self, *, refresh_token: str) -> tuple[str, str]:
        token_hash = sha256_hex(refresh_token)
        token_row = await self._refresh.get_active_by_hash(token_hash)
        if token_row is None:
            raise UnauthorizedError("Invalid refresh token")

        user = await self._users.get_by_id(token_row.user_id)
        if user is None or user.deleted_at is not None:
            raise UnauthorizedError("Invalid refresh token")

        # rotate refresh token (revoke old, issue new)
        await self._refresh.revoke_by_id(token_row.id)
        access = create_access_token(subject=user.id, token_version=user.token_version)
        new_refresh, expires_at = create_refresh_token(
            subject=user.id, token_version=user.token_version
        )
        await self._refresh.create(
            RefreshToken(
                user_id=user.id,
                token_hash=sha256_hex(new_refresh),
                expires_at=expires_at,
                revoked=False,
            )
        )
        await self._session.commit()
        return access, new_refresh

    async def logout(self, *, refresh_token: str) -> None:
        token_hash = sha256_hex(refresh_token)
        token_row = await self._refresh.get_active_by_hash(token_hash)
        if token_row is None:
            # idempotent logout
            return
        await self._refresh.revoke_by_id(token_row.id)
        await self._session.commit()

    async def revoke_all_sessions(self, *, user_id: str) -> None:
        user = await self._users.get_by_id(user_id)
        if user is None:
            return
        await self._users.update_token_version(user_id, user.token_version + 1)
        await self._refresh.revoke_all_for_user(user_id)
        await self._session.commit()
