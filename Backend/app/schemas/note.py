"""笔记 schema。"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="")
    category: str | None = Field(default=None, max_length=80)
    pinned: bool = False
    tags: List[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None
    category: str | None = Field(default=None, max_length=80)
    pinned: bool | None = None
    tags: List[str] | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    category: str | None
    pinned: bool
    tags: List[str]
    owner_id: int | None
    created_at: datetime
    updated_at: datetime


class NoteCount(BaseModel):
    total: int
