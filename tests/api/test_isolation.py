from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register", json={"email": email, "password": "Password123!", "full_name": "X"}
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Password123!"}
    )
    data = login.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.mark.anyio
async def test_user_isolation_accounts_categories_transactions(client: AsyncClient) -> None:
    h1 = await _register_and_login(client, "u1@example.com")
    h2 = await _register_and_login(client, "u2@example.com")

    acc = await client.post(
        "/api/v1/accounts",
        headers=h1,
        json={"name": "U1Acc", "type": "bank", "currency": "USD", "initial_balance": "100.00"},
    )
    assert acc.status_code == 201

    # other user cannot read account (should be 404 to avoid leakage)
    other_get = await client.get(f"/api/v1/accounts/{acc.json()['id']}", headers=h2)
    assert other_get.status_code == 404

    cat = await client.post(
        "/api/v1/categories", headers=h1, json={"name": "U1Cat", "type": "expense"}
    )
    assert cat.status_code == 201
    other_cat = await client.get(f"/api/v1/categories/{cat.json()['id']}", headers=h2)
    assert other_cat.status_code == 404

    now = datetime.now(timezone.utc).isoformat()
    tx = await client.post(
        "/api/v1/transactions",
        headers=h1,
        json={
            "type": "expense",
            "amount": "1.00",
            "occurred_at": now,
            "account_id": acc.json()["id"],
            "category_id": cat.json()["id"],
        },
    )
    assert tx.status_code == 201
    other_tx = await client.get(f"/api/v1/transactions/{tx.json()['id']}", headers=h2)
    assert other_tx.status_code == 404
