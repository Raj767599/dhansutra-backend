from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_transaction_income_expense_balance_rules(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    acc = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "Checking", "type": "bank", "currency": "USD", "initial_balance": "100.00"},
    )
    assert acc.status_code == 201
    account_id = acc.json()["id"]

    inc_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "SalaryX", "type": "income"}
    )
    exp_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "FoodX", "type": "expense"}
    )
    assert inc_cat.status_code == 201 and exp_cat.status_code == 201

    now = datetime.now(timezone.utc).isoformat()
    t1 = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "income",
            "amount": "50.00",
            "occurred_at": now,
            "account_id": account_id,
            "category_id": inc_cat.json()["id"],
        },
    )
    assert t1.status_code == 201, t1.text
    t2 = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "10.00",
            "occurred_at": now,
            "account_id": account_id,
            "category_id": exp_cat.json()["id"],
        },
    )
    assert t2.status_code == 201, t2.text

    acc_get = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert acc_get.status_code == 200
    assert Decimal(acc_get.json()["balance"]) == Decimal("140.00")

    # update expense to 20 -> should reduce balance by additional 10
    upd = await client.patch(
        f"/api/v1/transactions/{t2.json()['id']}", headers=auth_headers, json={"amount": "20.00"}
    )
    assert upd.status_code == 200
    acc_get2 = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert Decimal(acc_get2.json()["balance"]) == Decimal("130.00")

    # delete income -> reverse +50
    dele = await client.delete(f"/api/v1/transactions/{t1.json()['id']}", headers=auth_headers)
    assert dele.status_code == 204
    acc_get3 = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert Decimal(acc_get3.json()["balance"]) == Decimal("80.00")


@pytest.mark.anyio
async def test_transaction_transfer_rules(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    a1 = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "A1", "type": "bank", "currency": "USD", "initial_balance": "100.00"},
    )
    a2 = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "A2", "type": "cash", "currency": "USD", "initial_balance": "0.00"},
    )
    assert a1.status_code == 201 and a2.status_code == 201

    now = datetime.now(timezone.utc).isoformat()
    tx = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "transfer",
            "amount": "25.00",
            "occurred_at": now,
            "account_id": a1.json()["id"],
            "destination_account_id": a2.json()["id"],
        },
    )
    assert tx.status_code == 201, tx.text

    g1 = await client.get(f"/api/v1/accounts/{a1.json()['id']}", headers=auth_headers)
    g2 = await client.get(f"/api/v1/accounts/{a2.json()['id']}", headers=auth_headers)
    assert Decimal(g1.json()["balance"]) == Decimal("75.00")
    assert Decimal(g2.json()["balance"]) == Decimal("25.00")


@pytest.mark.anyio
async def test_transaction_list_pagination_and_search(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    acc = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "S", "type": "bank", "currency": "USD", "initial_balance": "1000.00"},
    )
    inc_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "Inc", "type": "income"}
    )
    now = datetime.now(timezone.utc).isoformat()
    for i in range(5):
        await client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "type": "income",
                "amount": "1.00",
                "occurred_at": now,
                "account_id": acc.json()["id"],
                "category_id": inc_cat.json()["id"],
                "note": f"note {i}",
            },
        )

    page = await client.get("/api/v1/transactions?limit=2&offset=0", headers=auth_headers)
    assert page.status_code == 200
    body = page.json()
    assert body["meta"]["limit"] == 2
    assert body["meta"]["offset"] == 0
    assert body["meta"]["total"] >= 5
    assert len(body["items"]) == 2

    search = await client.get("/api/v1/transactions?q=note%204", headers=auth_headers)
    assert search.status_code == 200
    assert any("note 4" in (t.get("note") or "") for t in search.json()["items"])
