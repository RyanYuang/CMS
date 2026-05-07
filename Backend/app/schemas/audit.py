"""审计日志 schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.audit_log import AuditAction


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor_id: int | None
    actor_username: str | None
    action: AuditAction
    target_type: str
    target_id: str | None
    summary: str | None
    diff: dict[str, Any] | None
    request_ip: str | None
    created_at: datetime
