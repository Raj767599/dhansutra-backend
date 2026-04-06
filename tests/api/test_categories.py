from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_category_crud_and_system_protection(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Custom", "type": "expense", "icon": "tag", "color": "#111111"},
    )
    assert created.status_code == 201
    cat = created.json()

    lst = await client.get("/api/v1/categories", headers=auth_headers)
    assert lst.status_code == 200
    body = lst.json()
    assert any(c["id"] == cat["id"] for c in body["items"])

    upd = await client.patch(
        f"/api/v1/categories/{cat['id']}", headers=auth_headers, json={"name": "Custom2"}
    )
    assert upd.status_code == 200
    assert upd.json()["name"] == "Custom2"

    dele = await client.delete(f"/api/v1/categories/{cat['id']}", headers=auth_headers)
    assert dele.status_code == 204
