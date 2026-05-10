"""文章 schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.models.article import ArticleStatus


class _AssetMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    public_url: str


class _CategoryMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class _TagMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class _AuthorMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: Optional[str] = None


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    summary: Optional[str] = Field(default=None, max_length=500)
    content: str = ""
    category_id: Optional[int] = None
    cover_asset_id: Optional[int] = None
    tag_ids: List[int] = Field(default_factory=list)
    status: ArticleStatus = ArticleStatus.draft


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    summary: Optional[str] = Field(default=None, max_length=500)
    content: Optional[str] = None
    category_id: Optional[int] = None
    cover_asset_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    note: Optional[str] = Field(default=None, max_length=255)


class ArticleStatusUpdate(BaseModel):
    status: ArticleStatus
    note: Optional[str] = Field(default=None, max_length=255)


class ArticleListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    summary: Optional[str]
    status: ArticleStatus
    published_at: Optional[datetime]
    cover: Optional[_AssetMini] = None
    category: Optional[_CategoryMini] = None
    author: Optional[_AuthorMini] = None
    tags: List[_TagMini] = Field(default_factory=list)
    view_count: int
    current_version: int
    created_at: datetime
    updated_at: datetime


class ArticleDetail(ArticleListItem):
    content: str


class ArticleVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    article_id: int
    version: int
    title: str
    slug: str
    summary: Optional[str]
    status: ArticleStatus
    note: Optional[str]
    operator_id: Optional[int]
    created_at: datetime
