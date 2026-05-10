"""资源 schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

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
    width: Optional[int]
    height: Optional[int]
    is_orphan: bool
    uploader_id: Optional[int]
    created_at: datetime


class AssetListItem(AssetOut):
    pass
