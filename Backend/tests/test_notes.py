"""笔记 CRUD + 置顶 + 越权 + 搜索过滤。"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_notes_crud_pin_search(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/notes",
        json={
            "title": "FastAPI 学习笔记",
            "content": "# 标题\n这是一段 **Markdown** 内容。",
            "category": "学习",
            "written_at": "2024-03-02T00:00:00+00:00",
            "tags": ["python", "fastapi"],
            "pinned": False,
        },
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text
    note = create.json()
    assert note["id"] > 0
    assert note["pinned"] is False
    assert note["tags"] == ["python", "fastapi"]
    assert note["written_at"] is not None
    assert note["written_at"].startswith("2024-03-02")
    note_id = note["id"]

    other = await client.post(
        "/api/v1/notes",
        json={"title": "Redis 备忘", "content": "缓存 key 设计", "tags": ["redis"]},
        headers=auth_headers,
    )
    assert other.status_code == 200
    other_id = other.json()["id"]

    update = await client.patch(
        f"/api/v1/notes/{note_id}",
        json={"title": "FastAPI 学习笔记 v2", "tags": ["python", "fastapi", "async"]},
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["title"] == "FastAPI 学习笔记 v2"
    assert "async" in update.json()["tags"]

    pin = await client.post(f"/api/v1/notes/{other_id}/pin", headers=auth_headers)
    assert pin.status_code == 200
    assert pin.json()["pinned"] is True

    listing = await client.get("/api/v1/notes", headers=auth_headers)
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert items, "笔记列表为空"
    assert items[0]["id"] == other_id

    search = await client.get("/api/v1/notes", params={"keyword": "FastAPI"}, headers=auth_headers)
    assert search.status_code == 200
    titles = [it["title"] for it in search.json()["items"]]
    assert any("FastAPI" in t for t in titles)

    tag_search = await client.get("/api/v1/notes", params={"keyword": "redis"}, headers=auth_headers)
    assert tag_search.status_code == 200
    assert any("Redis" in it["title"] for it in tag_search.json()["items"])

    cat_filter = await client.get("/api/v1/notes", params={"category": "学习"}, headers=auth_headers)
    assert cat_filter.status_code == 200
    assert all(it["category"] == "学习" for it in cat_filter.json()["items"])

    count = await client.get("/api/v1/notes/count", headers=auth_headers)
    assert count.status_code == 200
    assert count.json()["total"] >= 2

    delete = await client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert delete.status_code == 200

    after = await client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert after.status_code == 404


@pytest.mark.asyncio
async def test_viewer_cannot_write_notes(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    roles_resp = await client.get("/api/v1/roles", headers=auth_headers)
    viewer_role = next((r for r in roles_resp.json() if r["name"] == "viewer"), None)
    assert viewer_role is not None

    user_resp = await client.post(
        "/api/v1/users",
        json={
            "username": "noteviewer",
            "email": "noteviewer@example.com",
            "password": "viewerpass1",
            "full_name": "NoteViewer",
            "role_id": viewer_role["id"],
        },
        headers=auth_headers,
    )
    if user_resp.status_code != 409:
        assert user_resp.status_code == 200, user_resp.text

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "noteviewer", "password": "viewerpass1"},
    )
    assert login.status_code == 200
    viewer_token = login.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    can_read = await client.get("/api/v1/notes", headers=viewer_headers)
    assert can_read.status_code == 200

    write_resp = await client.post(
        "/api/v1/notes",
        json={"title": "viewer write", "content": "x"},
        headers=viewer_headers,
    )
    assert write_resp.status_code == 403
