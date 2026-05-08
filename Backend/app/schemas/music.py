"""音乐 schema。"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class MusicTrackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    artist: str | None = Field(default=None, max_length=200)
    album: str | None = Field(default=None, max_length=200)
    genre: str | None = Field(default=None, max_length=80)
    year: int | None = None
    duration_seconds: int | None = None
    cover_url: str | None = Field(default=None, max_length=500)
    audio_url: str | None = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    pinned: bool = False


class MusicTrackUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    artist: str | None = Field(default=None, max_length=200)
    album: str | None = Field(default=None, max_length=200)
    genre: str | None = Field(default=None, max_length=80)
    year: int | None = None
    duration_seconds: int | None = None
    cover_url: str | None = Field(default=None, max_length=500)
    audio_url: str | None = Field(default=None, max_length=500)
    tags: List[str] | None = None
    pinned: bool | None = None


class MusicTrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    artist: str | None
    album: str | None
    genre: str | None
    year: int | None
    duration_seconds: int | None
    cover_url: str | None
    audio_url: str | None
    tags: List[str]
    pinned: bool
    owner_id: int | None
    created_at: datetime
    updated_at: datetime


class MusicTrackCount(BaseModel):
    total: int
