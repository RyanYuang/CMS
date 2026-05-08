"""电影 schema。"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    original_title: str | None = Field(default=None, max_length=200)
    director: str | None = Field(default=None, max_length=120)
    cast: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    year: int | None = None
    duration_minutes: int | None = None
    rating: str | None = Field(default=None, max_length=20)
    synopsis: str = Field(default="")
    cover_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    pinned: bool = False


class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    original_title: str | None = Field(default=None, max_length=200)
    director: str | None = Field(default=None, max_length=120)
    cast: List[str] | None = None
    genres: List[str] | None = None
    year: int | None = None
    duration_minutes: int | None = None
    rating: str | None = Field(default=None, max_length=20)
    synopsis: str | None = None
    cover_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    tags: List[str] | None = None
    pinned: bool | None = None


class MovieOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    original_title: str | None
    director: str | None
    cast: List[str]
    genres: List[str]
    year: int | None
    duration_minutes: int | None
    rating: str | None
    synopsis: str
    cover_url: str | None
    video_url: str | None
    tags: List[str]
    pinned: bool
    owner_id: int | None
    created_at: datetime
    updated_at: datetime


class MovieCount(BaseModel):
    total: int
