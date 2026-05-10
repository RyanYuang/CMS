"""电影 schema。"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings

_ALLOWED_STILL_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def _validate_stills(values: List[str]) -> List[str]:
    if len(values) > settings.movie_still_max_count:
        raise ValueError(f"静帧最多 {settings.movie_still_max_count} 张")
    normalized: list[str] = []
    for value in values:
        still = (value or "").strip()
        if not still:
            continue
        lower = still.split("?", 1)[0].lower()
        if not lower.endswith(_ALLOWED_STILL_EXTENSIONS):
            raise ValueError("静帧仅支持 jpg/png/webp 格式")
        normalized.append(still)
    return normalized


class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    original_title: Optional[str] = Field(default=None, max_length=200)
    director: Optional[str] = Field(default=None, max_length=120)
    cast: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    duration_minutes: Optional[int] = None
    rating: Optional[str] = Field(default=None, max_length=20)
    synopsis: str = Field(default="")
    cover_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    stills: List[str] = Field(default_factory=list, max_length=settings.movie_still_max_count)
    tags: List[str] = Field(default_factory=list)
    pinned: bool = False

    @field_validator("stills")
    @classmethod
    def validate_stills(cls, value: List[str]) -> List[str]:
        return _validate_stills(value)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    original_title: Optional[str] = Field(default=None, max_length=200)
    director: Optional[str] = Field(default=None, max_length=120)
    cast: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    year: Optional[int] = None
    duration_minutes: Optional[int] = None
    rating: Optional[str] = Field(default=None, max_length=20)
    synopsis: Optional[str] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    stills: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    pinned: Optional[bool] = None

    @field_validator("stills")
    @classmethod
    def validate_stills(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        return _validate_stills(value)


class MovieOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    original_title: Optional[str]
    director: Optional[str]
    cast: List[str]
    genres: List[str]
    year: Optional[int]
    duration_minutes: Optional[int]
    rating: Optional[str]
    synopsis: str
    cover_url: Optional[str]
    video_url: Optional[str]
    stills: List[str]
    tags: List[str]
    pinned: bool
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class MovieCount(BaseModel):
    total: int
