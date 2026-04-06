from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_goal_crud_and_contributions(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    create = await client.post(
        "/api/v1/goals",
        headers=auth_headers,
        json={"name": "G1", "target_amount": "200.00", "currency": "USD", "deadline": now},
    )
    assert create.status_code == 201, create.text
    goal = create.json()
    assert goal["current_amount"] in ("0", 0, "0.00", 0.0)

    contrib = await client.post(
        f"/api/v1/goals/{goal['id']}/contributions",
        headers=auth_headers,
        json={"amount": "50.00", "contributed_at": now, "note": "first"},
    )
    assert contrib.status_code == 201

    get1 = await client.get(f"/api/v1/goals/{goal['id']}", headers=auth_headers)
    assert get1.status_code == 200
    assert float(get1.json()["current_amount"]) == 50.0
    assert len(get1.json()["contributions"]) == 1

    dele = await client.delete(f"/api/v1/goals/{goal['id']}", headers=auth_headers)
    assert dele.status_code == 204
