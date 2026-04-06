from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_dashboard_summary(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    acc = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "DAcc", "type": "bank", "currency": "USD", "initial_balance": "100.00"},
    )
    inc_cat = await client.post(
        "/api/v1/categories", headers=auth_headers, json={"name": "DInc", "type": "income"}
    )
    now = datetime.now(timezone.utc).isoformat()
    await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "type": "income",
            "amount": "10.00",
            "occurred_at": now,
            "account_id": acc.json()["id"],
            "category_id": inc_cat.json()["id"],
        },
    )

    r = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "total_balance" in body
    assert "recent_transactions" in body
    assert isinstance(body["account_overview"], list)
