from __future__ import annotations

import enum


class AccountType(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    card = "card"
    savings = "savings"
    investment = "investment"
    e_wallet = "e_wallet"


class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"


class ThemePreference(str, enum.Enum):
    system = "system"
    light = "light"
    dark = "dark"


class NotificationType(str, enum.Enum):
    budget_alert = "budget_alert"
    goal_deadline = "goal_deadline"
    recurring_reminder = "recurring_reminder"
