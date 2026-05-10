"""分类 schema。"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: Optional[str] = Field(default=None, max_length=120, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=80)
    slug: Optional[str] = Field(default=None, max_length=120, pattern=r"^[a-z0-9][a-z0-9\-]*$")
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[int]
    sort_order: int
