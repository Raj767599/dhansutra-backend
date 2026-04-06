from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_login_me_refresh_logout(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "u@example.com", "password": "Password123!", "full_name": "User"},
    )
    assert r.status_code == 201, r.text
    login = await client.post(
        "/api/v1/auth/login", json={"email": "u@example.com", "password": "Password123!"}
    )
    assert login.status_code == 200, login.text
    tokens = login.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == "u@example.com"

    refresh = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh.status_code == 200
    tokens2 = refresh.json()
    assert tokens2["access_token"] != tokens["access_token"]

    out = await client.post("/api/v1/auth/logout", json={"refresh_token": tokens2["refresh_token"]})
    assert out.status_code == 204


@pytest.mark.anyio
async def test_invalid_login(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": "x@example.com", "password": "Password123!", "full_name": "X"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "x@example.com", "password": "wrongwrong"}
    )
    assert login.status_code == 401
