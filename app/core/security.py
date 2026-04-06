from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_access_token(*, subject: str, token_version: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload: dict[str, Any] = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": subject,
        "type": "access",
        "tv": token_version,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid4()),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    return str(token)


def create_refresh_token(*, subject: str, token_version: int) -> tuple[str, datetime]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)
    token = str(uuid4()) + "." + str(uuid4())
    # refresh token is opaque; we persist only its hash in DB
    return token, expire


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload_any = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as e:
        raise UnauthorizedError("Invalid token") from e
    if not isinstance(payload_any, dict):
        raise UnauthorizedError("Invalid token")
    payload: dict[str, Any] = payload_any
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")
    return payload
