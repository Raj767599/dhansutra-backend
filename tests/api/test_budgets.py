from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_budget_crud_and_calculation(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    acc = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "BAcc", "type": "bank", "currency": "USD", "initial_balance": "1000.00"},
    )
    exp_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "BFood", "type": "expense"}
    )
    assert acc.status_code == 201 and exp_cat.status_code == 201

    now = datetime.now(timezone.utc)
    create = await client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "year": now.year,
            "month": now.month,
            "amount": "100.00",
            "currency": "USD",
            "category_id": exp_cat.json()["id"],
        },
    )
    assert create.status_code == 201, create.text
    b = create.json()
    assert b["spent"] in ("0", 0, "0.00", 0.0)

    tx = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "25.00",
            "occurred_at": now.isoformat(),
            "account_id": acc.json()["id"],
            "category_id": exp_cat.json()["id"],
        },
    )
    assert tx.status_code == 201

    get1 = await client.get(f"/api/v1/budgets/{b['id']}", headers=auth_headers)
    assert get1.status_code == 200
    assert float(get1.json()["spent"]) == 25.0

    dele = await client.delete(f"/api/v1/budgets/{b['id']}", headers=auth_headers)
    assert dele.status_code == 204
