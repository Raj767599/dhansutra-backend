"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-04-06

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("token_version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index(op.f("ix_users_deleted_at"), "users", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "accounts",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("balance", sa.Numeric(precision=18, scale=2), server_default="0", nullable=False),
        sa.Column("archived", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("allow_transactions_when_archived", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.CheckConstraint("balance >= 0", name="ck_accounts_balance_nonnegative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_archived"), "accounts", ["archived"], unique=False)
    op.create_index(op.f("ix_accounts_currency"), "accounts", ["currency"], unique=False)
    op.create_index(op.f("ix_accounts_deleted_at"), "accounts", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_accounts_type"), "accounts", ["type"], unique=False)
    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"], unique=False)
    op.create_index("ix_accounts_user_active", "accounts", ["user_id", "deleted_at", "archived"], unique=False)

    op.create_table(
        "categories",
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("icon", sa.String(length=80), nullable=True),
        sa.Column("color", sa.String(length=16), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_deleted_at"), "categories", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_categories_is_system"), "categories", ["is_system"], unique=False)
    op.create_index(op.f("ix_categories_type"), "categories", ["type"], unique=False)
    op.create_index(op.f("ix_categories_user_id"), "categories", ["user_id"], unique=False)
    op.create_index("ix_categories_user_type_active", "categories", ["user_id", "type", "deleted_at"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
    )
    op.create_index(op.f("ix_refresh_tokens_deleted_at"), "refresh_tokens", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_expires_at"), "refresh_tokens", ["expires_at"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_revoked"), "refresh_tokens", ["revoked"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"], unique=False)
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"], unique=False)

    op.create_table(
        "settings",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("preferred_currency", sa.String(length=3), nullable=False),
        sa.Column("locale", sa.String(length=20), server_default="en-US", nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default="UTC", nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("budget_alerts_enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("theme_preference", sa.String(length=10), server_default="system", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_settings_user_id"),
    )
    op.create_index(op.f("ix_settings_deleted_at"), "settings", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_settings_preferred_currency"), "settings", ["preferred_currency"], unique=False)
    op.create_index(op.f("ix_settings_user_id"), "settings", ["user_id"], unique=False)

    op.create_table(
        "budgets",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("category_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "year", "month", "category_id", name="uq_budgets_period_category"),
    )
    op.create_index(op.f("ix_budgets_category_id"), "budgets", ["category_id"], unique=False)
    op.create_index(op.f("ix_budgets_currency"), "budgets", ["currency"], unique=False)
    op.create_index(op.f("ix_budgets_deleted_at"), "budgets", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_budgets_user_id"), "budgets", ["user_id"], unique=False)
    op.create_index("ix_budgets_user_period", "budgets", ["user_id", "year", "month"], unique=False)

    op.create_table(
        "savings_goals",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("target_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("current_amount", sa.Numeric(precision=18, scale=2), server_default="0", nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.CheckConstraint("current_amount >= 0", name="ck_goals_current_nonnegative"),
        sa.CheckConstraint("target_amount > 0", name="ck_goals_target_positive"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_savings_goals_completed"), "savings_goals", ["completed"], unique=False)
    op.create_index(op.f("ix_savings_goals_currency"), "savings_goals", ["currency"], unique=False)
    op.create_index(op.f("ix_savings_goals_deadline"), "savings_goals", ["deadline"], unique=False)
    op.create_index(op.f("ix_savings_goals_deleted_at"), "savings_goals", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_savings_goals_user_id"), "savings_goals", ["user_id"], unique=False)
    op.create_index("ix_goals_user_active", "savings_goals", ["user_id", "deleted_at", "completed"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("body", sa.String(length=1000), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_deleted_at"), "notifications", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_notifications_read"), "notifications", ["read"], unique=False)
    op.create_index(op.f("ix_notifications_scheduled_for"), "notifications", ["scheduled_for"], unique=False)
    op.create_index(op.f("ix_notifications_type"), "notifications", ["type"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_index("ix_notifications_user_unread", "notifications", ["user_id", "read", "deleted_at"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("merchant", sa.String(length=120), nullable=True),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("destination_account_id", sa.String(length=36), nullable=True),
        sa.Column("category_id", sa.String(length=36), nullable=True),
        sa.Column("recurring_template", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["destination_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_account_id"), "transactions", ["account_id"], unique=False)
    op.create_index(op.f("ix_transactions_category_id"), "transactions", ["category_id"], unique=False)
    op.create_index(op.f("ix_transactions_currency"), "transactions", ["currency"], unique=False)
    op.create_index(op.f("ix_transactions_deleted_at"), "transactions", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_transactions_destination_account_id"), "transactions", ["destination_account_id"], unique=False)
    op.create_index(op.f("ix_transactions_occurred_at"), "transactions", ["occurred_at"], unique=False)
    op.create_index(op.f("ix_transactions_type"), "transactions", ["type"], unique=False)
    op.create_index(op.f("ix_transactions_user_id"), "transactions", ["user_id"], unique=False)
    op.create_index("ix_transactions_user_account", "transactions", ["user_id", "account_id"], unique=False)
    op.create_index("ix_transactions_user_category", "transactions", ["user_id", "category_id"], unique=False)
    op.create_index("ix_transactions_user_datetime", "transactions", ["user_id", "occurred_at"], unique=False)
    op.create_index("ix_transactions_user_type", "transactions", ["user_id", "type"], unique=False)

    op.create_table(
        "goal_contributions",
        sa.Column("goal_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("contributed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_goal_contrib_amount_positive"),
        sa.ForeignKeyConstraint(["goal_id"], ["savings_goals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_goal_contributions_contributed_at"), "goal_contributions", ["contributed_at"], unique=False)
    op.create_index(op.f("ix_goal_contributions_deleted_at"), "goal_contributions", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_goal_contributions_goal_id"), "goal_contributions", ["goal_id"], unique=False)


def downgrade() -> None:
    op.drop_table("goal_contributions")
    op.drop_table("transactions")
    op.drop_table("notifications")
    op.drop_table("savings_goals")
    op.drop_table("budgets")
    op.drop_table("settings")
    op.drop_table("refresh_tokens")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("users")

