"""笔记 schema。"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="")
    category: Optional[str] = Field(default=None, max_length=80)
    pinned: bool = False
    tags: List[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    content: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=80)
    pinned: Optional[bool] = None
    tags: Optional[List[str]] = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    category: Optional[str]
    pinned: bool
    tags: List[str]
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class NoteCount(BaseModel):
    total: int
