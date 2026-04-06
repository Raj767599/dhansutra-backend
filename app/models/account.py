from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AccountType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Account(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_accounts_balance_nonnegative"),
        Index("ix_accounts_user_active", "user_id", "deleted_at", "archived"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)

    balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default="0"
    )

    archived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0", index=True
    )
    allow_transactions_when_archived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )

    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction",
        back_populates="account",
        foreign_keys="Transaction.account_id",
    )
    incoming_transfers = relationship(
        "Transaction",
        back_populates="destination_account",
        foreign_keys="Transaction.destination_account_id",
    )

    @staticmethod
    def validate_type(value: str) -> str:
        AccountType(value)  # raises if invalid
        return value
