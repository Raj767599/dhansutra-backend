from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    raise RuntimeError("Use db_session_from_request instead")


async def db_session_from_request(request: Request) -> AsyncGenerator[AsyncSession, None]:
    db = request.app.state.db
    async for s in db.session():
        yield s


async def current_user(
    session: AsyncSession = Depends(db_session_from_request),
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> User:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError()
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    token_version = payload.get("tv")
    if not isinstance(user_id, str) or not isinstance(token_version, int):
        raise UnauthorizedError("Invalid token payload")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or user.deleted_at is not None:
        raise UnauthorizedError("User not found")
    if user.token_version != token_version:
        raise UnauthorizedError("Token revoked")
    return user
