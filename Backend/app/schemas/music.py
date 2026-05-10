"""音乐 schema。"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class MusicTrackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    artist: Optional[str] = Field(default=None, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=80)
    year: Optional[int] = None
    duration_seconds: Optional[int] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)
    audio_url: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    pinned: bool = False


class MusicTrackUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    artist: Optional[str] = Field(default=None, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=80)
    year: Optional[int] = None
    duration_seconds: Optional[int] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)
    audio_url: Optional[str] = Field(default=None, max_length=500)
    tags: Optional[List[str]] = None
    pinned: Optional[bool] = None


class MusicTrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    artist: Optional[str]
    album: Optional[str]
    genre: Optional[str]
    year: Optional[int]
    duration_seconds: Optional[int]
    cover_url: Optional[str]
    audio_url: Optional[str]
    tags: List[str]
    pinned: bool
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class MusicTrackCount(BaseModel):
    total: int
