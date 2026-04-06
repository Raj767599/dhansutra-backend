from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import TransactionType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Transaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        Index("ix_transactions_user_datetime", "user_id", "occurred_at"),
        Index("ix_transactions_user_account", "user_id", "account_id"),
        Index("ix_transactions_user_category", "user_id", "category_id"),
        Index("ix_transactions_user_type", "user_id", "type"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    merchant: Mapped[str | None] = mapped_column(String(120), nullable=True)

    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), index=True)
    destination_account_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("accounts.id"), nullable=True, index=True
    )
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=True, index=True
    )

    # Optional metadata for future recurring flows; no scheduler required.
    recurring_template: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
    destination_account = relationship(
        "Account", back_populates="incoming_transfers", foreign_keys=[destination_account_id]
    )
    category = relationship("Category", back_populates="transactions")

    @staticmethod
    def validate_type(value: str) -> str:
        TransactionType(value)
        return value
