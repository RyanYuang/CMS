"""文件上传与孤儿清理用例（RYA-12/15）。"""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient


def _png_bytes() -> bytes:
    # 1x1 红色 PNG（base64 解出来的最小图）
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
        "890000000d49444154789c63f8cf00000003000100"
        "5b1ee2120000000049454e44ae426082"
    )


@pytest.mark.asyncio
async def test_upload_and_orphan_cleanup(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    files = {"file": ("a.png", io.BytesIO(_png_bytes()), "image/png")}
    upload = await client.post("/api/v1/assets/upload", files=files, headers=auth_headers)
    assert upload.status_code == 200, upload.text
    asset = upload.json()
    assert asset["kind"] == "image"
    assert asset["public_url"].endswith(".png")

    listing = await client.get("/api/v1/assets?is_orphan=true", headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()["meta"]["total"] >= 1

    create = await client.post(
        "/api/v1/articles",
        json={"title": "with cover", "content": "x", "cover_asset_id": asset["id"]},
        headers=auth_headers,
    )
    assert create.status_code == 200, create.text

    cleanup = await client.post(
        "/api/v1/assets/cleanup-orphans?dry_run=true", headers=auth_headers
    )
    assert cleanup.status_code == 200


@pytest.mark.asyncio
async def test_reject_too_large_file(client: AsyncClient, auth_headers: dict[str, str], monkeypatch) -> None:
    from app.config import settings as app_settings

    monkeypatch.setattr(app_settings, "max_upload_mb", 0)
    files = {"file": ("big.bin", io.BytesIO(b"\x00" * 1024), "application/octet-stream")}
    resp = await client.post("/api/v1/assets/upload", files=files, headers=auth_headers)
    assert resp.status_code == 400
