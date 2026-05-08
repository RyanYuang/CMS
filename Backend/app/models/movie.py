"""电影模型。"""

from __future__ import annotations

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
    original_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    director: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cast: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[str | None] = mapped_column(String(20), nullable=True)
    synopsis: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
