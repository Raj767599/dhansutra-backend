from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SavingsGoal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "savings_goals"
    __table_args__ = (
        CheckConstraint("target_amount > 0", name="ck_goals_target_positive"),
        CheckConstraint("current_amount >= 0", name="ck_goals_current_nonnegative"),
        Index("ix_goals_user_active", "user_id", "deleted_at", "completed"),
    )

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=0, server_default="0"
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0", index=True
    )

    user = relationship("User", back_populates="savings_goals")
    contributions = relationship(
        "GoalContribution", back_populates="goal", cascade="all, delete-orphan"
    )


class GoalContribution(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "goal_contributions"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_goal_contrib_amount_positive"),)

    goal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("savings_goals.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    contributed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    goal = relationship("SavingsGoal", back_populates="contributions")
