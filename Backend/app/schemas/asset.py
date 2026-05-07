"""资源 schema。"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.asset import AssetKind


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    public_url: str
    kind: AssetKind
    mime_type: str
    size_bytes: int
    width: int | None
    height: int | None
    is_orphan: bool
    uploader_id: int | None
    created_at: datetime


class AssetListItem(AssetOut):
    pass
