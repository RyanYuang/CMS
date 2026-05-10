"""资源服务：上传、孤儿清理（RYA-12 / RYA-15）。"""

from __future__ import annotations

import hashlib
import io
import re
import secrets
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, BinaryIO

import aiofiles
from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import BizError, NotFound
from app.models import Article, Asset, AssetKind, User


_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}
_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg"}
_DOC_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


def _classify(mime: str) -> AssetKind:
    if mime in _IMAGE_TYPES:
        return AssetKind.image
    if mime in _VIDEO_TYPES:
        return AssetKind.video
    if mime in _AUDIO_TYPES:
        return AssetKind.audio
    if mime in _DOC_TYPES:
        return AssetKind.document
    return AssetKind.other


def _build_storage_key(filename: str) -> tuple[Path, str]:
    today = datetime.now(tz=timezone.utc).strftime("%Y/%m/%d")
    safe_name = Path(filename).name.replace(" ", "_")
    suffix = Path(safe_name).suffix
    stem = Path(safe_name).stem[:80]
    token = secrets.token_hex(6)
    rel = f"{today}/{stem}-{token}{suffix}"
    full = settings.upload_path / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    return full, rel


async def save_file(
    session: AsyncSession,
    *,
    file: BinaryIO,
    filename: str,
    content_type: str,
    uploader: Optional[User],
) -> Asset:
    raw = file.read()
    if not raw:
        raise BizError("空文件")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(raw) > max_bytes:
        raise BizError(f"文件大小超过限制 {settings.max_upload_mb}MB")

    full_path, rel_key = _build_storage_key(filename or "file")
    async with aiofiles.open(full_path, "wb") as fp:
        await fp.write(raw)

    width, height = (None, None)
    kind = _classify(content_type or "")
    if kind is AssetKind.image:
        try:
            with Image.open(io.BytesIO(raw)) as img:
                width, height = img.size
        except UnidentifiedImageError:
            pass

    digest = hashlib.sha256(raw).hexdigest()
    public_url = f"{settings.public_base_url.rstrip('/')}/static/uploads/{rel_key}"

    asset = Asset(
        filename=Path(filename).name,
        storage_key=rel_key,
        public_url=public_url,
        kind=kind,
        mime_type=content_type or "application/octet-stream",
        size_bytes=len(raw),
        width=width,
        height=height,
        checksum=digest,
        is_orphan=True,
        uploader_id=uploader.id if uploader else None,
    )
    session.add(asset)
    await session.flush()
    return asset


async def mark_used(session: AsyncSession, asset_ids: list[int]) -> None:
    if not asset_ids:
        return
    stmt = select(Asset).where(Asset.id.in_(asset_ids))
    res = await session.execute(stmt)
    for asset in res.scalars():
        asset.is_orphan = False


async def remove_asset(session: AsyncSession, asset_id: int) -> None:
    asset = await session.get(Asset, asset_id)
    if not asset:
        raise NotFound("资源不存在")

    full = settings.upload_path / asset.storage_key
    if full.exists():
        try:
            full.unlink()
        except OSError:
            pass

    await session.delete(asset)


async def cleanup_orphans(session: AsyncSession, *, dry_run: bool = False) -> dict[str, int]:
    """删除未被任何文章引用的孤儿资源。"""
    used_cover_ids = {row[0] for row in (
        await session.execute(select(Article.cover_asset_id).where(Article.cover_asset_id.isnot(None)))
    ).all()}

    stmt = select(Asset)
    rows = (await session.execute(stmt)).scalars().all()

    candidates = [a for a in rows if a.id not in used_cover_ids]
    removed = 0
    for asset in candidates:
        asset.is_orphan = True
        if not dry_run:
            full = settings.upload_path / asset.storage_key
            if full.exists():
                try:
                    full.unlink()
                except OSError:
                    pass
            await session.delete(asset)
            removed += 1
    return {"scanned": len(rows), "orphans": len(candidates), "removed": removed}
