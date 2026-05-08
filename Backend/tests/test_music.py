"""音乐 CRUD + 置顶 + 越权 + 搜索过滤分页。"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_music_crud_pin_search(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/music",
        json={
            "title": "夜空中最亮的星",
            "artist": "逃跑计划",
            "album": "世界",
            "genre": "流行",
            "year": 2011,
            "duration_seconds": 272,
            "cover_url": "https://example.com/song.jpg",
            "audio_url": "https://example.com/song.mp3",
            "tags": ["rock", "live"],
            "pinned": False,
        },
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text
    track = create.json()
    track_id = track["id"]

    create2 = await client.post(
        "/api/v1/music",
        json={"title": "追光者", "artist": "岑宁儿", "genre": "流行", "tags": ["ballad"]},
        headers=auth_headers,
    )
    assert create2.status_code == 200
    track2_id = create2.json()["id"]

    update = await client.patch(
        f"/api/v1/music/{track_id}",
        json={"duration_seconds": 280, "tags": ["rock", "classic"]},
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["duration_seconds"] == 280
    assert "classic" in update.json()["tags"]

    pin = await client.post(f"/api/v1/music/{track2_id}/pin", headers=auth_headers)
    assert pin.status_code == 200
    assert pin.json()["pinned"] is True

    listing = await client.get("/api/v1/music", headers=auth_headers)
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert items[0]["id"] == track2_id

    search = await client.get("/api/v1/music", params={"keyword": "逃跑计划"}, headers=auth_headers)
    assert search.status_code == 200
    assert any(row["id"] == track_id for row in search.json()["items"])

    genre_filter = await client.get("/api/v1/music", params={"genre": "流行"}, headers=auth_headers)
    assert genre_filter.status_code == 200
    assert all(row["genre"] == "流行" for row in genre_filter.json()["items"])

    page = await client.get("/api/v1/music", params={"page": 1, "page_size": 1}, headers=auth_headers)
    assert page.status_code == 200
    assert len(page.json()["items"]) == 1
    assert page.json()["meta"]["total"] >= 2

    count = await client.get("/api/v1/music/count", headers=auth_headers)
    assert count.status_code == 200
    assert count.json()["total"] >= 2

    delete = await client.delete(f"/api/v1/music/{track_id}", headers=auth_headers)
    assert delete.status_code == 200

    after = await client.get(f"/api/v1/music/{track_id}", headers=auth_headers)
    assert after.status_code == 404


@pytest.mark.asyncio
async def test_viewer_cannot_write_music(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    roles_resp = await client.get("/api/v1/roles", headers=auth_headers)
    viewer_role = next((r for r in roles_resp.json() if r["name"] == "viewer"), None)
    assert viewer_role is not None

    user_resp = await client.post(
        "/api/v1/users",
        json={
            "username": "musicviewer",
            "email": "musicviewer@example.com",
            "password": "viewerpass1",
            "full_name": "MusicViewer",
            "role_id": viewer_role["id"],
        },
        headers=auth_headers,
    )
    if user_resp.status_code != 409:
        assert user_resp.status_code == 200, user_resp.text

    login = await client.post("/api/v1/auth/login", json={"username": "musicviewer", "password": "viewerpass1"})
    assert login.status_code == 200
    viewer_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    can_read = await client.get("/api/v1/music", headers=viewer_headers)
    assert can_read.status_code == 200

    write_resp = await client.post("/api/v1/music", json={"title": "viewer music"}, headers=viewer_headers)
    assert write_resp.status_code == 403
