from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import TransactionType


class TransactionCreateRequest(BaseModel):
    type: TransactionType
    amount: Decimal = Field(..., gt=0, examples=["12.50"])
    occurred_at: datetime = Field(..., examples=["2026-04-06T12:00:00Z"])
    account_id: str
    category_id: str | None = None
    destination_account_id: str | None = None
    note: str | None = Field(default=None, max_length=500)
    merchant: str | None = Field(default=None, max_length=120)
    recurring_template: str | None = Field(
        default=None,
        max_length=2000,
        description="Opaque JSON string for future recurring UI; no scheduler.",
    )


class TransactionUpdateRequest(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    occurred_at: datetime | None = None
    account_id: str | None = None
    category_id: str | None = None
    destination_account_id: str | None = None
    note: str | None = Field(default=None, max_length=500)
    merchant: str | None = Field(default=None, max_length=120)
    recurring_template: str | None = Field(default=None, max_length=2000)


class TransactionResponse(BaseModel):
    id: str
    type: TransactionType
    amount: Decimal
    currency: str
    occurred_at: datetime
    note: str | None
    merchant: str | None
    account_id: str
    destination_account_id: str | None
    category_id: str | None


class TransactionListItem(TransactionResponse):
    pass


class TransactionOverviewResponse(BaseModel):
    start: datetime
    end: datetime
    total_income: Decimal
    total_expense: Decimal
    total_transfer_out: Decimal
    total_transfer_in: Decimal
    net_cashflow: Decimal
