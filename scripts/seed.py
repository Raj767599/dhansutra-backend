from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.app_factory import create_app
from app.core.security import hash_password
from app.domain.enums import AccountType, CategoryType, TransactionType
from app.models.account import Account
from app.models.budget import Budget
from app.models.category import Category
from app.models.savings_goal import GoalContribution, SavingsGoal
from app.models.setting import Setting
from app.models.transaction import Transaction
from app.models.user import User


async def seed() -> None:
    app = create_app()
    db = app.state.db

    async for session in db.session():
        # demo user
        email = os.getenv("DEMO_EMAIL", "demo@example.com")
        res = await session.execute(select(User).where(User.email == email))
        user = res.scalar_one_or_none()
        if user is None:
            user = User(
                email=email,
                password_hash=hash_password(os.getenv("DEMO_PASSWORD", "DemoPassword1!")),
                full_name="Demo User",
                onboarding_completed=True,
            )
            session.add(user)
            await session.flush()

            session.add(
                Setting(
                    user_id=user.id,
                    preferred_currency="USD",
                    locale="en-US",
                    timezone="UTC",
                    notifications_enabled=True,
                    budget_alerts_enabled=True,
                    theme_preference="system",
                )
            )

        # system default categories
        defaults = [
            ("Salary", CategoryType.income, "briefcase", "#22c55e"),
            ("Groceries", CategoryType.expense, "cart", "#f97316"),
            ("Rent", CategoryType.expense, "home", "#0ea5e9"),
            ("Transport", CategoryType.expense, "car", "#a855f7"),
            ("Dining", CategoryType.expense, "utensils", "#ef4444"),
        ]
        for name, ctype, icon, color in defaults:
            exists = await session.execute(
                select(Category).where(
                    Category.is_system.is_(True),
                    Category.name == name,
                    Category.type == ctype.value,
                )
            )
            if exists.scalar_one_or_none() is None:
                session.add(
                    Category(
                        user_id=None,
                        name=name,
                        type=ctype.value,
                        icon=icon,
                        color=color,
                        is_system=True,
                    )
                )

        await session.flush()

        # sample custom categories
        custom = [
            ("Side Hustle", CategoryType.income, "sparkles", "#10b981"),
            ("Subscriptions", CategoryType.expense, "repeat", "#64748b"),
        ]
        for name, ctype, icon, color in custom:
            exists = await session.execute(
                select(Category).where(
                    Category.user_id == user.id,
                    Category.name == name,
                    Category.type == ctype.value,
                    Category.deleted_at.is_(None),
                )
            )
            if exists.scalar_one_or_none() is None:
                session.add(
                    Category(
                        user_id=user.id,
                        name=name,
                        type=ctype.value,
                        icon=icon,
                        color=color,
                        is_system=False,
                    )
                )

        await session.flush()

        # accounts
        acc_res = await session.execute(
            select(Account).where(Account.user_id == user.id, Account.deleted_at.is_(None))
        )
        accounts = list(acc_res.scalars().all())
        has_cash = any(a.name == "Cash Wallet" for a in accounts)
        has_checking = any(a.name == "Main Checking" for a in accounts)
        if not has_cash:
            session.add(
                Account(
                    user_id=user.id,
                    name="Cash Wallet",
                    type=AccountType.cash.value,
                    currency="USD",
                    balance=Decimal("150.00"),
                    archived=False,
                    allow_transactions_when_archived=False,
                )
            )
        if not has_checking:
            session.add(
                Account(
                    user_id=user.id,
                    name="Main Checking",
                    type=AccountType.bank.value,
                    currency="USD",
                    balance=Decimal("2500.00"),
                    archived=False,
                    allow_transactions_when_archived=False,
                )
            )
        await session.flush()

        acc_res = await session.execute(
            select(Account).where(Account.user_id == user.id, Account.deleted_at.is_(None))
        )
        accounts = list(acc_res.scalars().all())
        cash = next(a for a in accounts if a.name == "Cash Wallet")
        checking = next(a for a in accounts if a.name == "Main Checking")

        # category lookup
        cat_res = await session.execute(select(Category).where(Category.deleted_at.is_(None)))
        all_cats = list(cat_res.scalars().all())
        groceries = next(
            c for c in all_cats if c.name == "Groceries" and c.type == CategoryType.expense.value
        )
        salary = next(
            c for c in all_cats if c.name == "Salary" and c.type == CategoryType.income.value
        )
        dining = next(
            c for c in all_cats if c.name == "Dining" and c.type == CategoryType.expense.value
        )

        # transactions (only insert if none exist)
        tx_res = await session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id, Transaction.deleted_at.is_(None)
            )
        )
        if tx_res.scalar_one_or_none() is None:
            now = datetime.now(timezone.utc)
            session.add_all(
                [
                    Transaction(
                        user_id=user.id,
                        type=TransactionType.income.value,
                        amount=Decimal("3000.00"),
                        currency="USD",
                        occurred_at=now - timedelta(days=10),
                        note="Monthly paycheck",
                        merchant="Employer Inc.",
                        account_id=checking.id,
                        destination_account_id=None,
                        category_id=salary.id,
                    ),
                    Transaction(
                        user_id=user.id,
                        type=TransactionType.expense.value,
                        amount=Decimal("54.20"),
                        currency="USD",
                        occurred_at=now - timedelta(days=3),
                        note="Weekly groceries",
                        merchant="Whole Foods",
                        account_id=checking.id,
                        destination_account_id=None,
                        category_id=groceries.id,
                    ),
                    Transaction(
                        user_id=user.id,
                        type=TransactionType.expense.value,
                        amount=Decimal("18.75"),
                        currency="USD",
                        occurred_at=now - timedelta(days=1),
                        note="Lunch",
                        merchant="Chipotle",
                        account_id=cash.id,
                        destination_account_id=None,
                        category_id=dining.id,
                    ),
                    Transaction(
                        user_id=user.id,
                        type=TransactionType.transfer.value,
                        amount=Decimal("100.00"),
                        currency="USD",
                        occurred_at=now - timedelta(days=2),
                        note="ATM withdrawal",
                        merchant=None,
                        account_id=checking.id,
                        destination_account_id=cash.id,
                        category_id=None,
                    ),
                ]
            )

            # apply balances to match transactions quickly (demo convenience)
            checking.balance = (
                Decimal("2500.00") + Decimal("3000.00") - Decimal("54.20") - Decimal("100.00")
            )
            cash.balance = Decimal("150.00") - Decimal("18.75") + Decimal("100.00")

        # budgets current month
        now = datetime.now(timezone.utc)
        bud_res = await session.execute(
            select(Budget).where(
                Budget.user_id == user.id,
                Budget.year == now.year,
                Budget.month == now.month,
                Budget.deleted_at.is_(None),
            )
        )
        if bud_res.scalar_one_or_none() is None:
            session.add(
                Budget(
                    user_id=user.id,
                    year=now.year,
                    month=now.month,
                    amount=Decimal("600.00"),
                    currency="USD",
                    category_id=None,
                )
            )
            session.add(
                Budget(
                    user_id=user.id,
                    year=now.year,
                    month=now.month,
                    amount=Decimal("300.00"),
                    currency="USD",
                    category_id=groceries.id,
                )
            )

        # savings goals + contributions
        goal_res = await session.execute(
            select(SavingsGoal).where(
                SavingsGoal.user_id == user.id, SavingsGoal.deleted_at.is_(None)
            )
        )
        goals = list(goal_res.scalars().all())
        if not goals:
            g = SavingsGoal(
                user_id=user.id,
                name="Emergency Fund",
                target_amount=Decimal("2000.00"),
                current_amount=Decimal("250.00"),
                currency="USD",
                deadline=now + timedelta(days=120),
                completed=False,
            )
            session.add(g)
            await session.flush()
            session.add_all(
                [
                    GoalContribution(
                        goal_id=g.id,
                        amount=Decimal("100.00"),
                        contributed_at=now - timedelta(days=20),
                        note="Initial",
                    ),
                    GoalContribution(
                        goal_id=g.id,
                        amount=Decimal("150.00"),
                        contributed_at=now - timedelta(days=5),
                        note="Extra savings",
                    ),
                ]
            )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
