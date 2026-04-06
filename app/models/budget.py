from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Budget(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
        UniqueConstraint(
            "user_id", "year", "month", "category_id", name="uq_budgets_period_category"
        ),
        Index("ix_budgets_user_period", "user_id", "year", "month"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)

    # optional category specific budget (expense categories only enforced in service)
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=True, index=True
    )

    user = relationship("User", back_populates="budgets")
    category = relationship("Category")
