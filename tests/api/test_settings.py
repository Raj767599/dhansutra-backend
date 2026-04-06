from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_settings_get_patch(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    r = await client.get("/api/v1/settings/me", headers=auth_headers)
    assert r.status_code == 200

    p = await client.patch(
        "/api/v1/settings/me",
        headers=auth_headers,
        json={"preferred_currency": "EUR", "theme_preference": "dark"},
    )
    assert p.status_code == 200
    assert p.json()["preferred_currency"] == "EUR"
    assert p.json()["theme_preference"] == "dark"
