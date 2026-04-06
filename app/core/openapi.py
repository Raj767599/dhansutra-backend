from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

OPENAPI_TAGS: list[dict[str, Any]] = [
    {
        "name": "auth",
        "description": "Authentication (register/login/refresh/logout) and token-based identity.",
    },
    {"name": "users", "description": "Current user profile management."},
    {"name": "dashboard", "description": "Home dashboard summary aggregates."},
    {"name": "accounts", "description": "Accounts/wallets/cards and balances."},
    {"name": "categories", "description": "System + user categories (income/expense)."},
    {
        "name": "transactions",
        "description": "Income/expense/transfer transactions with filters and summaries.",
    },
    {"name": "budgets", "description": "Monthly budgets with spent/remaining calculations."},
    {"name": "goals", "description": "Savings goals and contribution tracking."},
    {"name": "analytics", "description": "Aggregations for charts (cashflow, trends, categories)."},
    {
        "name": "settings",
        "description": "User preferences (currency, locale, notifications, theme).",
    },
]


def install_openapi(app: FastAPI) -> None:
    """
    Adds JWT Bearer security scheme so Swagger shows "Authorize",
    and provides tag metadata.

    Note: endpoint-level security requirements are inferred when
    Security(HTTPBearer()) is used in dependencies.
    """

    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})["bearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi  # type: ignore[method-assign]
