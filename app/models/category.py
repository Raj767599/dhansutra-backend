from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CategoryType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (Index("ix_categories_user_type_active", "user_id", "type", "deleted_at"),)

    # user_id is nullable for system categories (global defaults)
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)

    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0", index=True
    )

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

    @staticmethod
    def validate_type(value: str) -> str:
        CategoryType(value)
        return value
