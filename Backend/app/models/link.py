"""链接管理（CMS Frontend 链接管理页对应）。"""

from __future__ import annotations

import enum

from typing import Optional

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class LinkStatus(str, enum.Enum):
    online = "online"
    offline = "offline"


class LinkItem(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    cover: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    status: Mapped[LinkStatus] = mapped_column(
        Enum(LinkStatus, name="link_status"), default=LinkStatus.online, nullable=False, index=True
    )
