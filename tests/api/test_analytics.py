from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_analytics_endpoints(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    acc = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "AAcc", "type": "bank", "currency": "USD", "initial_balance": "100.00"},
    )
    inc_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "AInc", "type": "income"}
    )
    exp_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "AExp", "type": "expense"}
    )
    now = datetime.now(timezone.utc).isoformat()
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "income",
            "amount": "20.00",
            "occurred_at": now,
            "account_id": acc.json()["id"],
            "category_id": inc_cat.json()["id"],
        },
    )
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "expense",
            "amount": "5.00",
            "occurred_at": now,
            "account_id": acc.json()["id"],
            "category_id": exp_cat.json()["id"],
        },
    )

    s1 = await client.get("/api/v1/analytics/spending-by-category", headers=auth_headers)
    assert s1.status_code == 200

    s2 = await client.get("/api/v1/analytics/cashflow", headers=auth_headers)
    assert s2.status_code == 200
    assert float(s2.json()["net"]) == 15.0

    s3 = await client.get("/api/v1/analytics/top-categories?limit=3", headers=auth_headers)
    assert s3.status_code == 200

    s4 = await client.get("/api/v1/analytics/monthly-trend?months=6", headers=auth_headers)
    assert s4.status_code == 200
