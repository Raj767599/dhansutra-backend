from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import AccountType


class AccountCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Chase Checking"])
    type: AccountType
    currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])
    initial_balance: Decimal = Field(default=Decimal("0"), ge=0, examples=["1200.00"])
    archived: bool = False
    allow_transactions_when_archived: bool = False


class AccountUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    archived: bool | None = None
    allow_transactions_when_archived: bool | None = None


class AccountResponse(BaseModel):
    id: str
    name: str
    type: AccountType
    currency: str
    balance: Decimal
    archived: bool
    allow_transactions_when_archived: bool
