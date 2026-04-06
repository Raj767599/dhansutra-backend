from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserMeResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str | None
    onboarding_completed: bool


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    onboarding_completed: bool | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
