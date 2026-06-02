"""音乐 schema。"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings

_ALLOWED_PHOTO_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


class MusicStory(BaseModel):
    CN: Optional[str] = None
    EN: Optional[str] = None
    JP: Optional[str] = None


def _validate_photos(values: List[str]) -> List[str]:
    if len(values) > settings.movie_still_max_count:
        raise ValueError(f"照片最多 {settings.movie_still_max_count} 张")
    normalized: list[str] = []
    for value in values:
        photo = (value or "").strip()
        if not photo:
            continue
        lower = photo.split("?", 1)[0].lower()
        if not lower.endswith(_ALLOWED_PHOTO_EXTENSIONS):
            raise ValueError("照片仅支持 jpg/png/webp 格式")
        normalized.append(photo)
    return normalized


def _normalize_story(value: Optional[dict | MusicStory]) -> dict:
    if value is None:
        return {}
    if isinstance(value, MusicStory):
        payload = value.model_dump(exclude_none=True)
    elif isinstance(value, dict):
        payload = {k: v for k, v in value.items() if k in {"CN", "EN", "JP"} and v}
    else:
        return {}
    return {k: str(v).strip() for k, v in payload.items() if str(v).strip()}


class MusicTrackCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    artist: Optional[str] = Field(default=None, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=80)
    year: Optional[int] = None
    duration_seconds: Optional[int] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)
    audio_url: Optional[str] = Field(default=None, max_length=500)
    photos: List[str] = Field(default_factory=list, max_length=settings.movie_still_max_count)
    story: MusicStory | dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    pinned: bool = False

    @field_validator("photos")
    @classmethod
    def validate_photos(cls, value: List[str]) -> List[str]:
        return _validate_photos(value)

    @field_validator("story", mode="before")
    @classmethod
    def validate_story(cls, value) -> dict:
        return _normalize_story(value)


class MusicTrackUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    artist: Optional[str] = Field(default=None, max_length=200)
    album: Optional[str] = Field(default=None, max_length=200)
    genre: Optional[str] = Field(default=None, max_length=80)
    year: Optional[int] = None
    duration_seconds: Optional[int] = None
    cover_url: Optional[str] = Field(default=None, max_length=500)
    audio_url: Optional[str] = Field(default=None, max_length=500)
    photos: Optional[List[str]] = None
    story: Optional[MusicStory | dict] = None
    tags: Optional[List[str]] = None
    pinned: Optional[bool] = None

    @field_validator("photos")
    @classmethod
    def validate_photos(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        return _validate_photos(value)

    @field_validator("story", mode="before")
    @classmethod
    def validate_story(cls, value) -> Optional[dict]:
        if value is None:
            return None
        return _normalize_story(value)


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
    photos: List[str]
    story: dict
    tags: List[str]
    pinned: bool
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class MusicTrackCount(BaseModel):
    total: int
