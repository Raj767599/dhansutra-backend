from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="DhanSutra", validation_alias="APP_NAME")
    environment: Literal["local", "test", "staging", "prod"] = Field(
        default="local", validation_alias="ENVIRONMENT"
    )
    debug: bool = Field(default=False, validation_alias="DEBUG")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./finance.db", validation_alias="DATABASE_URL"
    )

    jwt_issuer: str = Field(default="dhansutra", validation_alias="JWT_ISSUER")
    jwt_audience: str = Field(default="dhansutra-mobile", validation_alias="JWT_AUDIENCE")
    # Default keeps local dev/test bootstrappable; override in .env for real use.
    jwt_secret_key: str = Field(default="change-me-in-local-env", validation_alias="JWT_SECRET_KEY")
    jwt_access_token_expire_minutes: int = Field(
        default=15, validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30, validation_alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_json: bool = Field(default=True, validation_alias="LOG_JSON")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
