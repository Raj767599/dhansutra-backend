from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_update_change_password(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    me = await client.get("/api/v1/users/me", headers=auth_headers)
    assert me.status_code == 200

    upd = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"full_name": "New Name", "onboarding_completed": True},
    )
    assert upd.status_code == 200
    assert upd.json()["full_name"] == "New Name"
    assert upd.json()["onboarding_completed"] is True

    bad = await client.post(
        "/api/v1/users/change-password",
        headers=auth_headers,
        json={"current_password": "wrongwrong", "new_password": "Password999!"},
    )
    assert bad.status_code == 401

    ok = await client.post(
        "/api/v1/users/change-password",
        headers=auth_headers,
        json={"current_password": "Password123!", "new_password": "Password999!"},
    )
    assert ok.status_code == 204
