from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx


@dataclass(frozen=True)
class Cfg:
    base_url: str
    email: str
    password: str


def _env(key: str, default: str) -> str:
    v = os.getenv(key)
    return v if v else default


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _print_ok(msg: str) -> None:
    print(f"OK  {msg}")


def _print_step(msg: str) -> None:
    print(f"\n== {msg}")


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _j(res: httpx.Response) -> Any:
    res.raise_for_status()
    return res.json()


def main() -> int:
    cfg = Cfg(
        base_url=_env("BASE_URL", "http://127.0.0.1:8000"),
        email=_env("DEMO_EMAIL", "demo@example.com"),
        password=_env("DEMO_PASSWORD", "DemoPassword1!"),
    )

    _print_step("Health checks")
    with httpx.Client(base_url=cfg.base_url, timeout=20.0) as client:
        r = client.get("/openapi.json")
        _assert(r.status_code == 200, "openapi.json not reachable")
        _print_ok("openapi.json reachable")

        r = client.get("/docs")
        _assert(r.status_code == 200, "docs not reachable")
        _print_ok("docs reachable")

        _print_step("Auth: login + me")
        login = _j(
            client.post(
                "/api/v1/auth/login",
                json={"email": cfg.email, "password": cfg.password},
            )
        )
        access = login["access_token"]
        _assert(isinstance(access, str) and access, "missing access_token")
        _print_ok("login")

        me = _j(client.get("/api/v1/auth/me", headers=_auth_headers(access)))
        _assert(me["email"] == cfg.email, "me email mismatch")
        _print_ok("me")

        _print_step("Accounts: create/list/get")
        acc = _j(
            client.post(
                "/api/v1/accounts",
                headers=_auth_headers(access),
                json={
                    "name": f"Smoke Account {datetime.now(timezone.utc).isoformat()}",
                    "type": "bank",
                    "currency": "USD",
                    "initial_balance": "0.00",
                    "archived": False,
                    "allow_transactions_when_archived": False,
                },
            )
        )
        account_id = acc["id"]
        _assert(isinstance(account_id, str) and account_id, "account id missing")
        _print_ok("create account")

        page_accounts = _j(
            client.get("/api/v1/accounts?limit=10&offset=0", headers=_auth_headers(access))
        )
        _assert("items" in page_accounts and "meta" in page_accounts, "accounts list not paginated")
        _print_ok("list accounts")

        _j(client.get(f"/api/v1/accounts/{account_id}", headers=_auth_headers(access)))
        _print_ok("get account")

        _print_step("Categories: create/list")
        cat = _j(
            client.post(
                "/api/v1/categories",
                headers=_auth_headers(access),
                json={
                    "name": f"Smoke Cat {datetime.now(timezone.utc).isoformat()}",
                    "type": "income",
                    "icon": "tag",
                    "color": "#64748b",
                },
            )
        )
        category_id = cat["id"]
        _assert(isinstance(category_id, str) and category_id, "category id missing")
        _print_ok("create category")

        page_categories = _j(
            client.get(
                "/api/v1/categories?type=expense&limit=10&offset=0", headers=_auth_headers(access)
            )
        )
        _assert(
            "items" in page_categories and "meta" in page_categories,
            "categories list not paginated",
        )
        _print_ok("list categories")

        _print_step("Transactions: create/list/detail/summary")
        occurred_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        tx = _j(
            client.post(
                "/api/v1/transactions",
                headers=_auth_headers(access),
                json={
                    "type": "income",
                    "amount": "100.00",
                    "currency": "USD",
                    "occurred_at": occurred_at,
                    "note": "Smoke test income",
                    "merchant": "Smoke Merchant",
                    "account_id": account_id,
                    "destination_account_id": None,
                    "category_id": category_id,
                },
            )
        )
        transaction_id = tx["id"]
        _assert(isinstance(transaction_id, str) and transaction_id, "transaction id missing")
        _print_ok("create transaction")

        page_tx = _j(
            client.get(
                "/api/v1/transactions?limit=10&offset=0&search=Smoke", headers=_auth_headers(access)
            )
        )
        _assert("items" in page_tx and "meta" in page_tx, "transactions list not paginated")
        _print_ok("list transactions")

        _j(client.get(f"/api/v1/transactions/{transaction_id}", headers=_auth_headers(access)))
        _print_ok("get transaction")

        _j(client.get("/api/v1/transactions/summary/overview", headers=_auth_headers(access)))
        _print_ok("transactions overview")

        _print_step("Budgets: create/list/get")
        now = datetime.now(timezone.utc)
        budget = _j(
            client.post(
                "/api/v1/budgets",
                headers=_auth_headers(access),
                json={
                    "year": now.year,
                    "month": now.month,
                    "amount": "100.00",
                    "currency": "USD",
                    "category_id": None,
                },
            )
        )
        budget_id = budget["id"]
        _assert(isinstance(budget_id, str) and budget_id, "budget id missing")
        _print_ok("create budget")

        page_budgets = _j(
            client.get("/api/v1/budgets?limit=10&offset=0", headers=_auth_headers(access))
        )
        _assert("items" in page_budgets and "meta" in page_budgets, "budgets list not paginated")
        _print_ok("list budgets")

        _j(client.get(f"/api/v1/budgets/{budget_id}", headers=_auth_headers(access)))
        _print_ok("get budget")

        _print_step("Goals: create/list/get/contribute")
        goal = _j(
            client.post(
                "/api/v1/goals",
                headers=_auth_headers(access),
                json={
                    "name": f"Smoke Goal {now.isoformat()}",
                    "target_amount": "500.00",
                    "currency": "USD",
                    "deadline": (now + timedelta(days=30)).isoformat(),
                },
            )
        )
        goal_id = goal["id"]
        _assert(isinstance(goal_id, str) and goal_id, "goal id missing")
        _print_ok("create goal")

        page_goals = _j(
            client.get("/api/v1/goals?limit=10&offset=0", headers=_auth_headers(access))
        )
        _assert("items" in page_goals and "meta" in page_goals, "goals list not paginated")
        _print_ok("list goals")

        _j(client.get(f"/api/v1/goals/{goal_id}", headers=_auth_headers(access)))
        _print_ok("get goal")

        _j(
            client.post(
                f"/api/v1/goals/{goal_id}/contributions",
                headers=_auth_headers(access),
                json={
                    "amount": "25.00",
                    "contributed_at": datetime.now(timezone.utc).isoformat(),
                    "note": "Smoke contribution",
                },
            )
        )
        _print_ok("add goal contribution")

        _print_step("Dashboard + Analytics + Settings")
        _j(client.get("/api/v1/dashboard/summary", headers=_auth_headers(access)))
        _print_ok("dashboard summary")

        start = (now - timedelta(days=30)).isoformat()
        end = now.isoformat()
        _j(
            client.get(
                "/api/v1/analytics/spending-by-category",
                headers=_auth_headers(access),
                params={"start": start, "end": end},
            )
        )
        _print_ok("analytics spending-by-category")
        _j(
            client.get(
                "/api/v1/analytics/cashflow",
                headers=_auth_headers(access),
                params={"start": start, "end": end},
            )
        )
        _print_ok("analytics cashflow")
        _j(
            client.get(
                "/api/v1/analytics/monthly-trend",
                headers=_auth_headers(access),
                params={"months": 6},
            )
        )
        _print_ok("analytics monthly-trend")
        _j(
            client.get(
                "/api/v1/analytics/top-categories",
                headers=_auth_headers(access),
                params={"start": start, "end": end, "limit": 5},
            )
        )
        _print_ok("analytics top-categories")

        _j(client.get("/api/v1/settings/me", headers=_auth_headers(access)))
        _print_ok("get settings")
        _j(
            client.patch(
                "/api/v1/settings/me",
                headers=_auth_headers(access),
                json={"preferred_currency": "USD"},
            )
        )
        _print_ok("update settings")

    print("\nALL SMOKE TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
