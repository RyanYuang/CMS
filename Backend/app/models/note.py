"""笔记模型（Notes）。

对应 Figma 设计稿 src/app/pages/media/Notes.tsx 中的字段，
与 Article 解耦，作为独立的轻量 Markdown 笔记资源。
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (
        Index("ix_notes_pinned_updated", "pinned", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
