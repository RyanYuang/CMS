"""链接管理 + 审计日志（RYA-11）。"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_links_crud_and_audit(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post(
        "/api/v1/links",
        json={
            "title": "测试链接",
            "url": "https://example.com",
            "cover": "https://example.com/cover.png",
            "sort_order": 1,
            "status": "online",
        },
        headers=auth_headers,
    )
    assert create.status_code == 200
    link_id = create.json()["id"]

    audit = await client.get(
        f"/api/v1/audit?target_type=link&target_id={link_id}",
        headers=auth_headers,
    )
    assert audit.status_code == 200
    assert audit.json()["meta"]["total"] >= 1

    public = await client.get("/api/v1/public/links")
    assert public.status_code == 200
    assert any(item["id"] == link_id for item in public.json())

    delete = await client.delete(f"/api/v1/links/{link_id}", headers=auth_headers)
    assert delete.status_code == 200
