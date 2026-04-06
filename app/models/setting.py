from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import ThemePreference
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Setting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("user_id", name="uq_settings_user_id"),)

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    preferred_currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(
        String(20), nullable=False, default="en-US", server_default="en-US"
    )
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, default="UTC", server_default="UTC"
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )
    budget_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )

    theme_preference: Mapped[str] = mapped_column(
        String(10), nullable=False, default="system", server_default="system"
    )

    user = relationship("User", back_populates="settings")

    @staticmethod
    def validate_theme(value: str) -> str:
        ThemePreference(value)
        return value
