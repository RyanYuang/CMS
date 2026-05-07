"""链接管理 schema。"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.link import LinkStatus


class LinkCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    url: str = Field(min_length=1, max_length=500)
    cover: str | None = None
    sort_order: int = 0
    status: LinkStatus = LinkStatus.online


class LinkUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    url: str | None = Field(default=None, max_length=500)
    cover: str | None = None
    sort_order: int | None = None
    status: LinkStatus | None = None


class LinkReorder(BaseModel):
    ordered_ids: list[int]


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    url: str
    cover: str | None
    sort_order: int
    status: LinkStatus
    updated_at: datetime
