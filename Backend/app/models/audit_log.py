"""审计日志（RYA-11）。"""

from __future__ import annotations

import enum

from typing import Optional

from sqlalchemy import Enum, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AuditAction(str, enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"
    publish = "publish"
    unpublish = "unpublish"
    archive = "archive"
    restore = "restore"
    login = "login"
    logout = "logout"
    upload = "upload"
    rollback = "rollback"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_target", "target_type", "target_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actor_username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action"), nullable=False, index=True
    )
    target_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    diff: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    request_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
