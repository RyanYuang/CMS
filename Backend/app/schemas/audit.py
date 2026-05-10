"""审计日志 schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, Any

from pydantic import BaseModel, ConfigDict

from app.models.audit_log import AuditAction


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor_id: Optional[int]
    actor_username: Optional[str]
    action: AuditAction
    target_type: str
    target_id: Optional[str]
    summary: Optional[str]
    diff: Optional[Dict[str, Any]]
    request_ip: Optional[str]
    created_at: datetime
