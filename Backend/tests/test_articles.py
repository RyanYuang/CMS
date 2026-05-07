"""文章 CRUD + 状态流转 + 版本管理用例（RYA-13/14）。"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_article_lifecycle(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/articles",
        json={
            "title": "我的第一篇文章",
            "summary": "短摘要",
            "content": "# Hello\n\n正文内容",
            "status": "draft",
        },
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text
    article = create.json()
    article_id = article["id"]
    assert article["status"] == "draft"
    assert article["current_version"] == 1

    upd = await client.patch(
        f"/api/v1/articles/{article_id}",
        json={"title": "更新后的标题", "content": "# Hi\n\n新正文"},
        headers=auth_headers,
    )
    assert upd.status_code == 200
    assert upd.json()["current_version"] == 2

    publish = await client.post(
        f"/api/v1/articles/{article_id}/status",
        json={"status": "published", "note": "first publish"},
        headers=auth_headers,
    )
    assert publish.status_code == 200
    assert publish.json()["status"] == "published"
    slug = publish.json()["slug"]

    public = await client.get(f"/api/v1/public/articles/{slug}")
    assert public.status_code == 200
    assert public.json()["status"] == "published"

    versions = await client.get(f"/api/v1/articles/{article_id}/versions", headers=auth_headers)
    assert versions.status_code == 200
    assert len(versions.json()) >= 3

    earliest_version = versions.json()[-1]["version"]
    rollback = await client.post(
        f"/api/v1/articles/{article_id}/rollback/{earliest_version}",
        headers=auth_headers,
    )
    assert rollback.status_code == 200

    listing = await client.get(
        "/api/v1/articles?keyword=更新后的&status=published&page=1&page_size=10",
        headers=auth_headers,
    )
    # 已 rollback，标题已改回旧值，但分页接口应可正常响应
    assert listing.status_code == 200


@pytest.mark.asyncio
async def test_invalid_status_transition(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/articles",
        json={"title": "状态机测试", "content": "ok"},
        headers=auth_headers,
    )
    article_id = create.json()["id"]
    archive_first = await client.post(
        f"/api/v1/articles/{article_id}/status",
        json={"status": "archived"},
        headers=auth_headers,
    )
    assert archive_first.status_code == 200

    bad = await client.post(
        f"/api/v1/articles/{article_id}/status",
        json={"status": "published"},
        headers=auth_headers,
    )
    assert bad.status_code == 400
