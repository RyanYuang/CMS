"""标签 schema。"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    slug: Optional[str] = Field(default=None, max_length=80, pattern=r"^[a-z0-9][a-z0-9\-]*$")


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
