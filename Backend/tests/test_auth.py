"""鉴权与 RBAC 越权用例（RYA-8）。"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success_and_me(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123456"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    payload = me.json()
    assert payload["username"] == "admin"
    assert "article:write" in payload["permissions"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_anonymous_cannot_access_protected(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/articles")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_viewer_cannot_write(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    roles_resp = await client.get("/api/v1/roles", headers=auth_headers)
    assert roles_resp.status_code == 200
    viewer_role = next((r for r in roles_resp.json() if r["name"] == "viewer"), None)
    assert viewer_role is not None, "viewer 内置角色未初始化"

    user_resp = await client.post(
        "/api/v1/users",
        json={
            "username": "viewer1",
            "email": "viewer1@example.com",
            "password": "viewerpass1",
            "full_name": "Viewer",
            "role_id": viewer_role["id"],
        },
        headers=auth_headers,
    )
    if user_resp.status_code != 409:
        assert user_resp.status_code == 200, user_resp.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "viewer1", "password": "viewerpass1"},
    )
    assert login.status_code == 200
    viewer_token = login.json()["access_token"]

    write_resp = await client.post(
        "/api/v1/articles",
        json={"title": "viewer write attempt", "content": "x"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert write_resp.status_code == 403
