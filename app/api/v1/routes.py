from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routers import (
    accounts,
    analytics,
    auth,
    budgets,
    categories,
    dashboard,
    goals,
    settings,
    transactions,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
