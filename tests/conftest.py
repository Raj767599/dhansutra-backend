from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.app_factory import create_app
from app.core.security import hash_password
from app.domain.enums import AccountType, CategoryType
from app.models.account import Account
from app.models.base import Base
from app.models.category import Category
from app.models.setting import Setting
from app.models.user import User


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture()
async def app(tmp_path) -> AsyncGenerator[object, None]:
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
    db_path = tmp_path / "test.db"
    a = create_app(database_url=f"sqlite+aiosqlite:///{db_path}")
    async with a.state.db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield a


@pytest.fixture()
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture()
async def user_and_token(client: AsyncClient) -> dict[str, str]:
    # register + login
    await client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "Password123!", "full_name": "A"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "a@example.com", "password": "Password123!"}
    )
    data = login.json()
    return {"access": data["access_token"], "refresh": data["refresh_token"]}


@pytest.fixture()
async def auth_headers(user_and_token: dict[str, str]) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_and_token['access']}"}


@pytest.fixture()
async def seeded_user(app) -> User:
    async for s in app.state.db.session():
        u = User(
            email="seed@example.com",
            password_hash=hash_password("Password123!"),
            full_name="Seed",
            onboarding_completed=True,
        )
        s.add(u)
        await s.flush()
        s.add(
            Setting(
                user_id=u.id,
                preferred_currency="USD",
                locale="en-US",
                timezone="UTC",
                notifications_enabled=True,
                budget_alerts_enabled=True,
                theme_preference="system",
            )
        )
        await s.commit()
        return u


@pytest.fixture()
async def account_category_fixtures(app, seeded_user: User) -> dict[str, str]:
    async for s in app.state.db.session():
        # reload user id
        u = await s.get(User, seeded_user.id)
        assert u is not None
        acc = Account(
            user_id=u.id,
            name="Checking",
            type=AccountType.bank.value,
            currency="USD",
            balance=Decimal("1000.00"),
            archived=False,
            allow_transactions_when_archived=False,
        )
        s.add(acc)
        cat_exp = Category(
            user_id=None,
            name="Groceries",
            type=CategoryType.expense.value,
            icon="cart",
            color="#fff",
            is_system=True,
        )
        cat_inc = Category(
            user_id=None,
            name="Salary",
            type=CategoryType.income.value,
            icon="briefcase",
            color="#000",
            is_system=True,
        )
        s.add_all([cat_exp, cat_inc])
        await s.flush()
        await s.commit()
        return {
            "user_id": u.id,
            "account_id": acc.id,
            "expense_cat_id": cat_exp.id,
            "income_cat_id": cat_inc.id,
        }
