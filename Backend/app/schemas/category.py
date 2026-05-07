"""分类 schema。"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str | None = Field(default=None, max_length=120, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    description: str | None = None
    parent_id: int | None = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    slug: str | None = Field(default=None, max_length=120, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    description: str | None = None
    parent_id: int | None = None
    sort_order: int | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: str | None
    parent_id: int | None
    sort_order: int
