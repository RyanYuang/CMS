"""电影模型。"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        Index("ix_movies_pinned_updated", "pinned", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    director: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    cast: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rating: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    work_category: Mapped[str] = mapped_column(String(20), nullable=False, default="feature", index=True)
    synopsis: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cover_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    stills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
