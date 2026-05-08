"""电影 CRUD + 置顶 + 越权 + 搜索过滤分页。"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_movies_crud_pin_search(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/movies",
        json={
            "title": "星际穿越",
            "original_title": "Interstellar",
            "director": "克里斯托弗·诺兰",
            "cast": ["马修·麦康纳", "安妮·海瑟薇"],
            "genres": ["科幻", "冒险"],
            "year": 2014,
            "duration_minutes": 169,
            "rating": "PG-13",
            "synopsis": "穿越虫洞寻找新家园",
            "cover_url": "https://example.com/interstellar.jpg",
            "video_url": "https://example.com/interstellar.mp4",
            "stills": [
                "https://example.com/interstellar-still-1.jpg",
                "https://example.com/interstellar-still-2.webp",
            ],
            "tags": ["nolan", "space"],
            "pinned": False,
        },
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text
    movie = create.json()
    movie_id = movie["id"]

    create2 = await client.post(
        "/api/v1/movies",
        json={"title": "盗梦空间", "director": "克里斯托弗·诺兰", "genres": ["科幻"], "tags": ["dream"]},
        headers=auth_headers,
    )
    assert create2.status_code == 200
    movie2_id = create2.json()["id"]

    update = await client.patch(
        f"/api/v1/movies/{movie_id}",
        json={"duration_minutes": 170, "tags": ["nolan", "space", "classic"]},
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["duration_minutes"] == 170
    assert "classic" in update.json()["tags"]
    assert update.json()["stills"] == [
        "https://example.com/interstellar-still-1.jpg",
        "https://example.com/interstellar-still-2.webp",
    ]

    pin = await client.post(f"/api/v1/movies/{movie2_id}/pin", headers=auth_headers)
    assert pin.status_code == 200
    assert pin.json()["pinned"] is True

    listing = await client.get("/api/v1/movies", headers=auth_headers)
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert items[0]["id"] == movie2_id

    search = await client.get("/api/v1/movies", params={"keyword": "Interstellar"}, headers=auth_headers)
    assert search.status_code == 200
    assert any(row["id"] == movie_id for row in search.json()["items"])

    genre_filter = await client.get("/api/v1/movies", params={"genre": "科幻"}, headers=auth_headers)
    assert genre_filter.status_code == 200
    assert all("科幻" in row["genres"] for row in genre_filter.json()["items"])

    page = await client.get("/api/v1/movies", params={"page": 1, "page_size": 1}, headers=auth_headers)
    assert page.status_code == 200
    assert len(page.json()["items"]) == 1
    assert page.json()["meta"]["total"] >= 2

    count = await client.get("/api/v1/movies/count", headers=auth_headers)
    assert count.status_code == 200
    assert count.json()["total"] >= 2

    delete = await client.delete(f"/api/v1/movies/{movie_id}", headers=auth_headers)
    assert delete.status_code == 200

    after = await client.get(f"/api/v1/movies/{movie_id}", headers=auth_headers)
    assert after.status_code == 404


@pytest.mark.asyncio
async def test_movies_update_stills_and_public_order(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/movies",
        json={"title": "静帧测试片", "stills": ["https://example.com/a.jpg", "https://example.com/b.png"]},
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text
    movie_id = create.json()["id"]

    update = await client.patch(
        f"/api/v1/movies/{movie_id}",
        json={"stills": ["https://example.com/c.webp", "https://example.com/a.jpg"]},
        headers=auth_headers,
    )
    assert update.status_code == 200, update.text
    assert update.json()["stills"] == ["https://example.com/c.webp", "https://example.com/a.jpg"]

    public_movies = await client.get("/api/v1/public/movies")
    assert public_movies.status_code == 200
    row = next((item for item in public_movies.json() if item["id"] == movie_id), None)
    assert row is not None
    assert row["stills"] == ["https://example.com/c.webp", "https://example.com/a.jpg"]


@pytest.mark.asyncio
async def test_movies_stills_validation(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    invalid_format = await client.post(
        "/api/v1/movies",
        json={"title": "格式错误", "stills": ["https://example.com/invalid.gif"]},
        headers=auth_headers,
    )
    assert invalid_format.status_code == 422

    too_many_stills = [f"https://example.com/{idx}.jpg" for idx in range(1, 22)]
    invalid_count = await client.post(
        "/api/v1/movies",
        json={"title": "数量过多", "stills": too_many_stills},
        headers=auth_headers,
    )
    assert invalid_count.status_code == 422


@pytest.mark.asyncio
async def test_viewer_cannot_write_movies(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    roles_resp = await client.get("/api/v1/roles", headers=auth_headers)
    viewer_role = next((r for r in roles_resp.json() if r["name"] == "viewer"), None)
    assert viewer_role is not None

    user_resp = await client.post(
        "/api/v1/users",
        json={
            "username": "movieviewer",
            "email": "movieviewer@example.com",
            "password": "viewerpass1",
            "full_name": "MovieViewer",
            "role_id": viewer_role["id"],
        },
        headers=auth_headers,
    )
    if user_resp.status_code != 409:
        assert user_resp.status_code == 200, user_resp.text

    login = await client.post("/api/v1/auth/login", json={"username": "movieviewer", "password": "viewerpass1"})
    assert login.status_code == 200
    viewer_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    can_read = await client.get("/api/v1/movies", headers=viewer_headers)
    assert can_read.status_code == 200

    write_resp = await client.post("/api/v1/movies", json={"title": "viewer movie"}, headers=viewer_headers)
    assert write_resp.status_code == 403
