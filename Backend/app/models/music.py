"""音乐模型。"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class MusicTrack(Base):
    __tablename__ = "music_tracks"
    __table_args__ = (
        Index("ix_music_tracks_pinned_updated", "pinned", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    artist: Mapped[str | None] = mapped_column(String(200), nullable=True)
    album: Mapped[str | None] = mapped_column(String(200), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(80), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
