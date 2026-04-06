from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_account_crud(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={"name": "Wallet", "type": "cash", "currency": "USD", "initial_balance": "10.00"},
    )
    assert create.status_code == 201, create.text
    acc = create.json()

    lst = await client.get("/api/v1/accounts", headers=auth_headers)
    assert lst.status_code == 200
    body = lst.json()
    assert any(a["id"] == acc["id"] for a in body["items"])

    get1 = await client.get(f"/api/v1/accounts/{acc['id']}", headers=auth_headers)
    assert get1.status_code == 200

    upd = await client.patch(
        f"/api/v1/accounts/{acc['id']}", headers=auth_headers, json={"archived": True}
    )
    assert upd.status_code == 200
    assert upd.json()["archived"] is True

    dele = await client.delete(f"/api/v1/accounts/{acc['id']}", headers=auth_headers)
    assert dele.status_code == 204


@pytest.mark.anyio
async def test_account_unauthorized(client: AsyncClient) -> None:
    r = await client.get("/api/v1/accounts")
    assert r.status_code == 401
